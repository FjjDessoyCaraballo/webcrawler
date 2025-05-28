import os
import base64
import re
import csv
import sqlite3
from urllib.parse import urljoin, urlparse
from typing import Optional, Tuple, List


class Fetcher:
	def __init__(self):
		self._conn: Optional[sqlite3.Connection] = None
	
	def EntryPoint(self, DbPath: str) -> bool:
		"""
		EntryPoint should be the only public method available for users to interact with `Fetcher`. Here we define the location of the
		database and the class should handle everything by itself, including outputting the csv resulting file at the end.

		:Parameters: DbPath a string containing the path to the database.

		:Returns: True if successful. False if errors were found before being able to connect to database.
		"""
		if not DbPath or not os.path.exists(DbPath):
			print(f'Error: database not found in path {DbPath}')
			return False
		try:
			self._conn = sqlite3.connect(DbPath)
			# Making the concious choice of not checking integrity of connection 
			# and if database is locked.
			Cursor = self._FetchRows()
			self._ProcessRows(Cursor)
			self._UnloadDatabaseToCsv()
			self._conn.close()
			return True
		except sqlite3.OperationalError as e:
			print(f'Database connection error: {e}')
			return False
		except Exception as e:
			print(f'Error: {e}')
			return False
	
	def _FetchRows(self) -> sqlite3.Cursor:
		"""
		Method to fetch data from our database. Specifically we are looking to query 
		for successful requests where the `fetch_status` was 200. In those cases we are
		going to store the results in a pointer SQLite3 `cursor` and return to `EntryPoint`.

		:Returns: cursor pointer to the SQLite3 query results 
		"""
		query = "SELECT id, domain, html_body, final_url FROM domains WHERE fetch_status == 200"
		cursor: sqlite3.Cursor = self._conn.execute(query)
		return cursor
	
	def _ProcessRows(self, Cursor: sqlite3.Cursor):
		"""
		Method for extracting and processing the html_body column. Additional information is being
		sent downstream, such as id and final_url to help facilitate error handling and processing 
		of the logo URL.

		:Parameter: Cursor sqlite3.Cursor type that points to the database.

		:Returns: None
		"""
		row: Tuple[int, str, str, str]
		processed: int = 0
		error: int = 0

		try:
			for row in Cursor:
				RowId, Domain, HtmlBody, FinalUrl = row
				print(f'[{RowId}] Attemping to extract logo for {Domain}')
				try:
					if self._ScanHtml(RowId, HtmlBody, FinalUrl):
						processed += 1
						print(f'[{RowId}] 🟢 extracted logo of {Domain}')
					else:
						error += 1
						print(f'[{RowId}] 🔴 Failed to extract logo for {Domain}')
				except Exception as e:
					error += 1
					print(f'[{RowId}] 🔴 Error processing {Domain}: {e}')
					continue

			self._conn.commit()
			print(f'\nTransaction completed: {processed} processed, {error} errors')
		except sqlite3.DatabaseError as e:
			self.conn.rollback()
			print(f'Transaction rolled back on database error: {e}')
		except Exception as e:
			self.conn.rollback()
			print(f'Transaction rolled back on unknown error: {e}')

	def _ScanHtml(self, RowId: int, HtmlBody: str, Domain: str) -> bool:
		"""
		Method to scan the HTML and find which method we are using to extract the logo. I'm using a waterfall
		method to try through different methodologies of extraction. If one succeeds we return.
		
		:Parameter: RowId integer representing which row of the database the HTML body is from.

		:Parameter: HtmlBody the index.html of given domain from the database.

		:Returns: None if no method was applicable, we return None
		"""
		Favicon: str

		# Find favicon as a temporary fallback alternative
		Favicon = self._FaviconExtraction(HtmlBody, Domain)
		if Favicon is not None:
			self._InsertFavicon(RowId, Favicon, 'FAVICON_LINK')

		PossibleLogo: Tuple[str, float] = []

		# 28th of May CURRENT ISSUE: SVGs got scored and any minimum match would be enough
		# Need to score them all together and fetch the highest scoring

		PossibleLogoSvg = self._SvgMethod(HtmlBody, Domain)
		PossibleLogoImg = self._ImgMethod(HtmlBody, Domain)

		AllResults = [PossibleLogoSvg, PossibleLogoImg]
		
		print(f'SVG SCORE: {PossibleLogoSvg[1] if PossibleLogoSvg is not None else "None"}')
		print(f'IMG SCORE: {PossibleLogoImg[1] if PossibleLogoImg is not None else "None"}')

		for result in AllResults:
			if result is not None:
				if isinstance(result, list):
					PossibleLogo.extend([r for r in result if r is not None])
				elif isinstance(result, tuple) and len(result) == 2:
					PossibleLogo.append(result)

		if not PossibleLogo:
			print(f'[{RowId}] No logo candidates found')
			return False
		
		WinnerPossibility = max(PossibleLogo, key=lambda x: x[1])

		if WinnerPossibility == PossibleLogoSvg:
			method = 'SVG_TAG'
		elif WinnerPossibility == PossibleLogoImg:
			method = 'IMG_TAG'
		# elif WinnerPossibility == PossibleLogoCustom:
		# 	method = 'CUSTOM_TAG'
		else:
			method = 'UNKNOWN'

		return self._InsertLogoIntoDb(RowId, WinnerPossibility[0], method, WinnerPossibility[1])

	def _SvgMethod(self, HtmlBody: str, Domain: str) -> Tuple[str, float]:
		"""
		Method #1 for logo extraction by converting SVG into URL data methodology using base64.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		LogoUrl: Tuple[str, float] = '', 0.0
		Score: float = 0.0
		AllSvgs: List[Tuple[str, str]] = []

		AllSvgs = self._FindAllTags(HtmlBody, r'(.{0,200})<svg[^>]*>.*?</svg>(.{0,200})')
		
		if not AllSvgs:
			return None
		
		ScoredSvgs: List[Tuple[str, float]] = []

		for Content, Context in AllSvgs:
			Score = self._CalculateProbabilityScore(Content, Context)
			if Score > 0:
				ScoredSvgs.append((Content, Score))
		
		# AI used here: helped with the lambda syntax in max
		# There's still a chance to have two same score WinnerSvgs
		WinnerSvg = max(ScoredSvgs, key=lambda x: x[1])
		LogoUrl = self._SvgToDataUrl(WinnerSvg[0])
		return (LogoUrl, WinnerSvg[1])

	def _SvgToDataUrl(self, SvgContent: str) -> str:
		"""
		Convert SVG to browser-accessible data URL

		:Parameter: SvgContent a string of the HTML SVG tag containing the logo

		:Returns: base64 logo URL
		"""
		SvgClean = SvgContent.strip()
		SvgBytes = SvgClean.encode('utf-8')
		SvgBase64 = base64.b64encode(SvgBytes).decode('utf-8')
		return f'data:image/svg+xml;base64,{SvgBase64}'

	def _CalculateProbabilityScore(self, Content: str, Context: str) -> float:
		"""
		Method to calculate the likelihood that the tag we got contains a logo. The scale
		goes form zero (0) to one (1).

		:Parameter: Content is a string that contains the content inside the tag.
		
		:Parameter: Context is a string that contains everything between opening and closing svg tag.

		:Returns: FinalScore is a float which dictates how fair the extract scored.
		"""
		Score: float = 0.0
		
		# Make everything lower case to have a standard baseline
		ContentLowerCase = Content.lower()
		ContextLowerCase = Context.lower()

		# AI used: I used AI to find a way to structure a scoring point system for the SVGs
		# so the values are a bit arbitrary
		PositiveIndicators = {
			# Direct references to logo
			'logo': 0.4,
			'brand': 0.3,
			'company': 0.2,

			# Structural indicators (usually you can see logos in the headers)
			'header': 0.2,
			'nav': 0.2,
			'navbar': 0.2,
			'top': 0.1,

			# Semantic indicators
			# 'src=' 0.2 # SVGs apparently cannot do src
			'aria-label': 0.2,
			'title=': 0.1,
			'alt=': 0.1,

			# ID patterns
			'class="logo': 0.4,
			'id="logo': 0.4,
			'class="brand': 0.3,
			'class="header': 0.2,

			# tag specifics
    		'src="logo': 0.3, # IMG
        	'src="brand': 0.3, # IMG
        	'href="logo': 0.2, # A TAG
        	'href="#logo': 0.3, # A TAG
			'alt="logo': 0.3, # IMG
			'viewbox=': 0.1, # SVG
		}

		for indicator, weight in PositiveIndicators.items():
			if indicator in ContentLowerCase or indicator in ContextLowerCase:
				# If we find a string in the tag that says "logo", the indicator
				# will be a string called logo and the indicator will be the corresponding
				# score of "logo", which is 0.4 in our dictionary.
				# If there is a match, we add weight into our final score. 
				Score += weight

		# Use of AI: Also used AI to compile items for the negative indicators list.
		NegativeIndicators = {
			'icon': 0.2,
			'arrow': 0.3,
			'close': 0.4,
			'menu': 0.2,
			'search': 0.3,
			'social': 0.2,
			'footer': 0.2,
		}

		for indicator, penalty in NegativeIndicators.items():
			if indicator in ContentLowerCase or indicator in ContextLowerCase:
				# In the same way as we compiled the score with positive indicators, the
				# negative indicators are meant to keep us clear from false-positives.
				Score -= penalty

		return max(0.0, min(1.0, Score))

	def _FindAllTags(self, HtmlBody: str, Pattern: str) -> List[Tuple[str, str]]:
		"""
		Method for extraction of all tags that match the regex pattern.

		:Parameter: HtmlBody a string that contains the HTML body.

		:Parameter: pattern

		:Returns: AllTags list of tuples with content and context around the tags.
		"""
		AllTags = []

		# IGNORECASE - case insensitive
		# DOTALL - make dot match newlines too
		matches = re.finditer(Pattern, HtmlBody, re.DOTALL | re.IGNORECASE)

		for match in matches:
			BeforeContext = match.group(1)
			Content = match.group(0)[len(match.group(1)):-len(match.group(2))]
			AfterContext = match.group(2)

			Context = BeforeContext + AfterContext
			AllTags.append((Content, Context))

		return AllTags

	def _MakeAbsoluteUrl(self, Url: str, BaseUrl: str) -> str:
		"""
		The first parameter is the URL that was taken from a tag. Therefore we do not properly
		know what we might be getting. The second argument comes from our database, which we can
		expect to be correct since we are only working with the URLs where we had status code 200.

		:Parameter: Url a string that possibly is an URL to the logo

		:Parameter: BaseUrl a string of the domain taken from final_url in the database.

		:Returns: The method returns an absolute URL path to the image. If URL is absent it returns None.
		"""
		if not Url:
			return ''
		
		# Clause to check if path is already absolute
		if Url.startswith(('http://', 'https://', 'data:')):
			return Url
		
		AbsoluteUrl: str = ''

		# URL is protocol sensitive
		if Url.startswith('//'):
			ParsedBase = urlparse(BaseUrl)
			AbsoluteUrl = f'{ParsedBase.scheme}:{Url}'
			return AbsoluteUrl
		
		AbsoluteUrl = urljoin(BaseUrl, Url)
		
		return AbsoluteUrl

	def _ImgMethod(self, HtmlBody: str, Domain: str):
		"""
		Method #2 for logo extraction looking for `<img>` tags in the HTML body. This method is a first fallback
		from the SVG method, and maybe not as fruitful as the SvgMethod, but it is better than searching for other
		different tags. In sum, this method should score less than the SVG, but more than the custom tag method.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		imgs: list[Tuple[str, str]] = []

		imgs = self._FindAllTags(HtmlBody, r'(.{0,200})<img[^>]*>(.{0,200})')

		if not imgs:
			return None

		ScoredImg: list[Tuple[str, str, float]] = []
		for Content, Context in imgs:
			Score = self._CalculateProbabilityScore(Content, Context)
			if Score > 0:
				SourceMatch = re.search(r'src=["\']([^"\']+)["\']', Content, re.IGNORECASE)
				if SourceMatch:
					SourceUrl = SourceMatch.group(1)
					AbsoluteUrl = self._MakeAbsoluteUrl(SourceUrl, Domain)
					ScoredImg.append((AbsoluteUrl, Content, Score))
		
		if not ScoredImg:
			return None
		
		WinnerImg = max(ScoredImg, key=lambda x: x[2])

		return WinnerImg[0], WinnerImg[2]


	# def _CustomTagMethod(self, HtmlBody: str, Domain: str):
	# 	"""
	# 	Method #3 for logo extraction by searching for `a`, `div`, and `span` tags. This method is burdensome 
	# 	since divs are plentiful and the likelihood of finding the logo inside these tags is lower. Therefore
	# 	the confidence score of this method is lower.

	# 	:Parameter: HtmlBody string of the index.html of given domain in database.
		
	# 	:Parameter: Domain string containing the landing page/homepage of given domain.

	# 	:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
	# 	"""
	# 	aTags = self._FindAllTags(HtmlBody, r'(.{0,200})<a[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*style=["\'][^"\']*background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)[^"\']*["\'][^>]*>(.{0,200})')
	# 	Divs = self._FindAllTags(HtmlBody, r'(.{0,200})<div[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*style=["\'][^"\']*background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)[^"\']*["\'][^>]*>(.{0,200})')
	# 	Spans = self._FindAllTags(HtmlBody, r'(.{0,200})<span[^>]*class=["\'][^"\']*logo[^"\']*["\'][^>]*style=["\'][^"\']*background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)[^"\']*["\'][^>]*>(.{0,200})')

	# 	Patterns: list[Tuple[str, str]] = []
	# 	Patterns.extend(aTags)
	# 	Patterns.extend(Divs)
	# 	Patterns.extend(Spans)

	# 	if not Patterns:
	# 		return None

	# 	ScoredTag: list[Tuple[str, float]] = []

	# 	for Content, Context in Patterns:
	# 		Score = self._CalculateProbabilityScore(Content, Context)
	# 		if Score > 0:
	# 			BackgroundMatch = re.search(r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)', Content, re.IGNORECASE)
	# 			if BackgroundMatch:
	# 				SourceUrl = BackgroundMatch.group(1)
	# 				AbsoluteUrl = self._MakeAbsoluteUrl(SourceUrl, Domain)
	# 				ScoredTag.append((AbsoluteUrl, Content, Score))
		
	# 	if not ScoredTag:
	# 		return None

	# 	WinnerTag = max(ScoredTag, key=lambda x: x[2])
		
	# 	return WinnerTag[0], WinnerTag[2]

	def _InsertLogoIntoDb(self, RowId: int, LogoUrl: str, Method: str, Confidence: float) -> None:
		"""
		Method that exclusively deals with inserting logos into the database.

		:Parameter: RowId integer representing which row of the database the HTML body is from.
		
		:Parameter: LogoUrl URL that contains logo image.
		
		:Parameter: Method methodology used to obtain logo.
		
		:Returns: None
		"""
		try:
			self._conn.execute('''
						UPDATE domains
						SET logo_url = ?, extraction_method = ?, confidence_score = ?
						WHERE id = ?
						''', (LogoUrl, Method, Confidence, RowId))
			return True
		except sqlite3.IntegrityError as e:
			print(f"Database integrity error for row {RowId}: {e}")
			return False
		except sqlite3.OperationalError as e:
			print(f"Database operation failed for row {RowId}: {e}")
			return False
		except sqlite3.DatabaseError as e:
			print(f"Database error for row {RowId}: {e}")
			return False
		except Exception as e:
			print(f"Unexpected error updating row {RowId}: {e}")
			return False

	def _FaviconExtraction(self, HtmlBody: str, Domain: str) -> Optional[str]:
		"""
		Method to find and extract URL of favicon

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.
		
		:Returns: Favicon URL in string if successful. None is returned in case of failure.
		"""
		Favicon: str = ''
		patterns = [
			r'<link[^>]*rel=["\'](?:shortcut )?icon["\'][^>]*href=["\']([^"\']+)["\']',
			r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\'](?:shortcut )?icon["\']',
			r'<link[^>]*rel=["\']apple-touch-icon["\'][^>]*href=["\']([^"\']+)["\']'
		]

		for pattern in patterns:
			match = re.search(pattern, HtmlBody, re.IGNORECASE)
			if match:
				FaviconUrl = match.group(1)
				Favicon = self._MakeAbsoluteUrl(FaviconUrl, Domain)
				return Favicon

		## Fallback method (not going to include to the final submission because it may yield false results)
		# ParsedUrl = urlparse(Domain)
		# Favicon = f'{ParsedUrl.scheme}://{ParsedUrl.netloc}/favicon.ico'
		# return Favicon

		return None
	
	def _InsertFavicon(self, RowId: int, Favicon: str, Method: str) -> None:
		"""
		Method for insertion of favicon URL into database column favicon_url.

		:Parameter: RowId integer representing which row of the database the HTML body is from.

		:Parameter: Favicon URL in string format containing the address to the favicon.

		:Parameter: Method methodology used to obtain logo.
		"""
		try:
			self._conn.execute('''
						UPDATE domains
						SET favicon_url = ?, extraction_method = ?
						WHERE id = ?
						''', (Favicon, Method, RowId))
			print(f'[{RowId}] 🟡 Favicon extracted')
		except sqlite3.IntegrityError as e:
			print(f"Database integrity error for row {RowId}: {e}")
			return False
		except sqlite3.OperationalError as e:
			print(f"Database operation failed for row {RowId}: {e}")
			return False
		except sqlite3.DatabaseError as e:
			print(f"Database error for row {RowId}: {e}")
			return False
		except Exception as e:
			print(f"Unexpected error updating row {RowId}: {e}")
			return False

	def _UnloadDatabaseToCsv(self) -> bool:
		"""
		Method to output CSV transcription of resulting database after Fetcher operations are done. Takes no parameters.

		:Returns: True is successful. False if it fails.
		"""
		try:
			Cursor = self._conn.cursor()
			
			# Cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # gonna reformulate the SQL query
			CsvName = "websites_logos"
			
			Cursor.execute('''
				SELECT domain, logo_url, extraction_method, confidence_score, robots_txt 
				FROM domains
				''')
			data = Cursor.fetchall()
			
			with open(f"{CsvName}.csv", 'w', newline='', encoding='utf-8') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow(['domain', 'logo_url', 'extraction_method', 'confidence_score', 'robots_txt'])
				writer.writerows(data)
			
			print(f"Successfully exported to {CsvName}.csv")
			return True
			
		except Exception as e:
			print(f"Export failed: {str(e)}")
			return False
