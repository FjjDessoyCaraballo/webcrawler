import base64
import re
import csv
import sqlite3
import asyncio
from typing import Optional, Tuple, List, Union

class Fetcher:
	def __init__(self):
		self._conn: sqlite3.Connection = []
		self._rows = ()
	
	def EntryPoint(self, DbPath: str) -> bool:
		if DbPath == '':
			print('Error: database not found')
			return False
		try:
			self._conn = sqlite3.connect(DbPath)
			Cursor = self._FetchRows()
			asyncio(self._ProcessRows(Cursor))
			print('Executed to the end')
			self._conn.close()
			return True
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
	
	async def _ProcessRows(self, Cursor: sqlite3.Cursor):
		row: Tuple[int, str, str, str]
		for row in Cursor:
			RowId, Domain, HtmlBody, FinalUrl = row
			print(f'[{RowId}] Attemping to extract logo for {Domain}')
			if self._ScanHtml(RowId, HtmlBody, FinalUrl) == False:
				print(f'[{RowId}] 🔴 Failed to extract logo for {Domain}')
			print(f'[{RowId}] 🟢 extracted logo of {Domain}')

	async def _ScanHtml(self, RowId: int, HtmlBody: str, Domain: str) -> bool:
		"""
		Method to scan the HTML and find which method we are using to extract the logo.
		
		:Parameter: RowId integer representing which row of the database the HTML body is from.

		:Parameter: HtmlBody the index.html of given domain from the database.

		:Returns: None if no method was applicable, we return None
		"""
		LogoUrl: str
		Favicon: str

		# Find favicon as a temporary fallback alternative
		Favicon = self._FaviconExtraction(HtmlBody, Domain)
		if Favicon is not None:
			self._InsertFavicon(RowId, Favicon, 'FAVICON_LINK')

		# Method 1: SVG tags
		LogoUrl = self._SvgMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'SVG_TAG', 0.8)
			return True

		# Method 2: img tags
		LogoUrl = self._ImgMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'IMG_TAG', 0.6)
			return True
		
		# Method 3: custom tags
		LogoUrl = self._CustomTagMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'CUSTOM_TAG', 0.3)
			return True

		return False

	async def _SvgMethod(self, HtmlBody: str, Domain: str):
		"""
		Method #1 for logo extraction by converting SVG into URL data methodology using base64.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		LogoUrl: str = ''
		Score: float = 0.0
		AllSvgs: List[Tuple[str, str]] = []

		AllSvgs = self._FindAllSvgs(HtmlBody)
		
		if not AllSvgs:
			return None
		
		ScoredSvgs: List[Tuple[str, str]] = []

		for SvgContent, Context in AllSvgs:
			Score = self._CalculateProbabilityScore(SvgContent, Context)
			if Score > 0:
				ScoredSvgs.append(SvgContent, Score)
		
		# AI used here: helped with the lambda syntax in max
		WinnerSvg = max(ScoredSvgs, key=lambda x: x[1])[0]
		LogoUrl = self._SvgToDataUrl(WinnerSvg)
		return LogoUrl

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

	async def _CalculateProbabilityScore(self, Content: str, Context: str) -> float:
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

			# Source patterns
    		'src="logo': 0.3,
        	'src="brand': 0.3,
        	'href="logo': 0.2,
        	'href="#logo': 0.3,
		}

		for indicator, weight in PositiveIndicators.items():
			if indicator in ContentLowerCase or indicator in ContextLowerCase:
				# If we find a string in the tag that says "logo", the indicator
				# will be a string called logo and the indicator will be the corresponding
				# score of "logo", which is 0.4 in our dictionary.
				# If there is a match, we add weight into our final score. 
				score += weight

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
				score -= penalty

		return max(0.0, min(1.0, score))

	async def _FindAllSvgs(self, HtmlBody: str) -> List[Tuple[str, str]]:
		svgs = []

		# regex pattern for SVG tags
		pattern = r'<svg[^>]*>.*?</svg>'

		# IGNORECASE - case insensitive
		# DOTALL - make dot match newlines too
		matches = re.finditer(pattern, HtmlBody, re.DOTALL | re.IGNORECASE)

		for match in matches:
			BeforeContext = match.group1(1)
			SvgContent = match.group(0)[len(match.group(1)):-len(match.group(2))]
			AfterContext = match.group(2)

			Context = BeforeContext + AfterContext
			svgs.append((SvgContent, Context))

		return svgs

	async def _ImgMethod(self, HtmlBody: str, Domain: str):
		"""
		Method #2 for logo extraction using XXX methodology that does Y.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		LogoUrl: str = ''
		return None
	
	

	async def _CustomTagMethod(self, HtmlBody: str, Domain: str):
		"""
		Method #3 for logo extraction using XXX methodology that does Y.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		LogoUrl: str = ''
		return None

	async def _InsertLogoIntoDb(self, RowId: int, LogoUrl: str, Method: str, Confidence: float) -> None:
		"""
		Method that exclusively deals with inserting logos into the database.

		:Parameter: RowId integer representing which row of the database the HTML body is from.
		
		:Parameter: LogoUrl URL that contains logo image.
		
		:Parameter: Method methodology used to obtain logo.
		
		:Returns: None
		"""
		self._conn.execute(''''
					UPDATE domains
					SET logo_url = ?, extraction_method = ?, confidence_score = ?
					WHERE id = ?
					''', (LogoUrl, Method, Confidence, RowId))

	async def _FaviconExtraction(self, HtmlBody: str, Domain: str) -> Optional[str]:
		"""
		Method to find and extract URL of favicon

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.
		
		:Returns: Favicon URL in string if successful. None is returned in case of failure.
		"""
		Favicon: str = ''
		return Favicon
	
	async def _InsertFavicon(self, RowId: int, Favicon: str, Method: str) -> None:
		"""
		Method for insertion of favicon URL into database column favicon_url.

		:Parameter: RowId integer representing which row of the database the HTML body is from.

		:Parameter: Favicon URL in string format containing the address to the favicon.

		:Parameter: Method methodology used to obtain logo.
		"""
		self._conn.execute(''''
					UPDATE domains
					SET favicon_url = ?, extraction_method = ?
					WHERE id = ?
					''', (Favicon, Method, RowId))
		print(f'[{RowId}] 🟡 Favicon extracted')

	def UnloadDatabaseToCsv(self):
		"""
		Method to output CSV transcription of resulting database after Fetcher operations are done. Takes no parameters.

		:Returns: True is successful. False if it fails.
		"""
		try:
			Cursor = self._conn.cursor()
			
			# Cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # gonna reformulate the SQL query
			TableName = Cursor.fetchone()[0]
			
			Cursor.execute(f"SELECT * FROM {TableName}")
			data = Cursor.fetchall()
			
			ColumnNames = [description[0] for description in Cursor.description]
			
			with open(f"{TableName}.csv", 'w', newline='', encoding='utf-8') as csvfile:
				writer = csv.writer(csvfile)
				
				writer.writerow(ColumnNames)
				
				writer.writerows(data)
			
			print(f"Successfully exported to {TableName}.csv")
			return True
			
		except Exception as e:
			print(f"Export failed: {str(e)}")
			return False
