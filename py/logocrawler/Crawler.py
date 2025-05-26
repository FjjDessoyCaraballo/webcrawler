import os
import csv
import sqlite3
import aiohttp
import ssl
import asyncio
# import random ## FOR TESTING PURPOSES

class Crawler:
	def __init__(self):
		self._Entries: list[str] = []
		self._DbPath = 'logos.db'
		self._InitDb()

	def _InitDb(self):
		"""
		Database initialization for storing the `index.html` files from each of the listed domains. Takes no parameters
		nor returns anything.
		"""
		conn = sqlite3.connect(self._DbPath)
		conn.execute('''
			CREATE TABLE IF NOT EXISTS domains (
			   id INTEGER PRIMARY KEY,
			   domain TEXT UNIQUE,
			   robots_txt INTEGER CHECK (robots_txt IN (0, 1)),
			   html_body TEXT,
			   final_url TEXT,
			   logo_url TEXT,
			   favicon_url TEXT,
			   fetch_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			   fetch_status INTEGER,
			   error_type TEXT,
			   extraction_method TEXT,
			   confidence_score REAL
			)
		''')
		conn.commit()
		conn.close()

	def EntryPoint(self, Domains, mode) -> None:
		"""
		Entrypoint should be the only public function to avoid confusion. We will work
		with the bare minimum and work our way to the webscrapping after this.

		:Parameter: `Domains` If mode (1) is selected, domains contains a csv file, otherwise it is a single domain url.

		:Parameter: `mode` defines if we are working with a csv file (1) or single entry mode (2)

		:Returns: None
		"""
		if mode == 1:
			self._CsvEntry(Domains)
		elif mode == 2:	
			self._SingleEntry(Domains)
		asyncio.run(self._StoreRequests())

	async def _CheckRobotsTxt(self, session: aiohttp.ClientSession, domain: str) -> bool:
		"""
		Check if crawling is allowed according to robots.txt
		
		:Parameter: session - aiohttp session to use for the request

		:Parameter: domain - domain to check robots.txt for

		:Returns: True if crawling is allowed, False otherwise
		"""
		try:
			async with session.get(f'https://{domain}/robots.txt') as response:
				if response.status == 200:
					content = await response.text()
					return 'Disallow: /' not in content
		except:
			# If robots.txt is inaccessible, assume crawling is allowed
			pass
		return True


	async def _StoreRequests(self) -> None:
		"""
		Fetch the index.html file from all listed domains and insert them into the database.
		"""
		# Counters for visualization
		SuccessCounter: int = 0
		FailedCounter: int = 0

		# self._Entries = random.sample(self._Entries, 10) ## FOR TESTING PURPOSES

		conn = sqlite3.connect(self._DbPath)

		ssl_context = ssl.create_default_context()
		ssl_context.check_hostname = False
		ssl_context.verify_mode = ssl.CERT_NONE

		connector = aiohttp.TCPConnector(
			limit=100,
			limit_per_host=1,
			ttl_dns_cache=300,
			ssl_context=ssl_context
		)
		
		timeout = aiohttp.ClientTimeout(total=15, connect=10)
		
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'en-US,en;q=0.5',
			'Accept-Encoding': 'gzip, deflate',
			'Connection': 'keep-alive',
			'Upgrade-Insecure-Requests': '1',
    }

		async with aiohttp.ClientSession(
			connector=connector,
			timeout=timeout,
			headers=headers,
			read_bufsize=65536,
			max_line_size=16384,
			max_field_size=16384
		) as session:
			for domain in self._Entries:

				# Check if robots.txt exists first
				RobotsAllowed = await self._CheckRobotsTxt(session, domain)

				# Fallback method to differentiate between http and https
				SuccessUrl, StatusCode, HtmlContent = await self._FetchWithFallback(session, domain)

				if SuccessUrl and HtmlContent:
					conn.execute('''
					INSERT OR REPLACE INTO domains (
						domain, html_body, robots_txt, fetch_status, final_url
					) VALUES (?, ?, ?, ?, ?)
				''', (domain, HtmlContent, 1 if RobotsAllowed else 0, StatusCode, SuccessUrl))
					SuccessCounter += 1
					RobotsStatus = "✅" if RobotsAllowed else "☑️"
					print(f"{RobotsStatus} {domain} -> {SuccessUrl}: Success")
				elif StatusCode == -1:
					conn.execute('''
					INSERT OR REPLACE INTO domains (
						domain, fetch_status, error_type
					) VALUES (?, ?, ?)
				''', (domain, StatusCode, "DNS_RESOLUTION_FAILED"))
					FailedCounter += 1
					print(f"💀 {domain} does not exist")
				else:
					conn.execute('''
				  	INSERT OR REPLACE INTO domains (
				  		domain, fetch_status
				  ) VALUES (?, ?)
				''', (domain, StatusCode or 0))
					FailedCounter += 1
					print(f"❌ {domain}: Failed (Status : {StatusCode or 'Network Error'})")

				# If we sleep for 100ms we may avoid rate limiting. It adds up in the collection, but pays off in the long-term.
				# instead of fixed number (100ms) I could probably check the robots.txt for `Crawl-delay`. 
				await asyncio.sleep(0.1)
		
		conn.commit()
		conn.close()
		print(f"\nCompleted fetching {len(self._Entries)} domains")
		print(f"\n✅ Successfully fetched: {SuccessCounter}")
		print(f"\n❌ Failed to fetch: {FailedCounter}")

	async def _FetchWithFallback(self, session: aiohttp.ClientSession, domain: str):
		"""
		Try multiple URL variants for a domain.

		:Parameters: session information about contained session with given domain

		:Parameters: domain basic URL of the informed domain

		:Returns: Multiple first return value is the final url, second is the HTML status code, and the last is the index.html
		"""
		urls_to_try = [
			f'https://{domain}',
			f'http://{domain}',
			f'https://www.{domain}',
			f'http://www.{domain}'
		]
		
		for url in urls_to_try:
			try:
				async with session.get(url, allow_redirects=True) as response:
					if response.status == 200:
						html = await response.text()
						return url, response.status, html
			except aiohttp.ClientConnectorError as e:
				if "No address associated with hostname" in str(e):
					return None, -1, None
				continue
			except (aiohttp.ClientError, asyncio.TimeoutError, UnicodeDecodeError):
				continue # trying to minimize the output, therefore no printing here
			except Exception as e:
				continue # trying to minimize the output, therefore no printing here
		
		return None, 0, None	

	def _CsvEntry(self, Domains) -> None:
		"""
		This function is called when mode (1) was chosen. We proceed to parse the csv file.
		Any user faulty input will make the program exit during parsing time.

		:Parameter: `Domains` csv file that contains a list of domains for logo extraction.

		:Returns: None
		"""
		try:
			path = self._FindCsv(Domains)
			self._Entries = self._OpenCsv(path)
		except Exception as e:
			print(f"Error: {e}")
	
	def _OpenCsv(self, CsvPath) -> list[str]:
		"""
		Function to open and list out the domains, leaving blank spaces for later use when
		we retrieve the logos and favicons.

		:Parameters: `CsvPath` the absolute path to the csv file.

		:Returns: `Data` 
		"""
		with open(CsvPath, 'r') as CsvFile:
			Reader = csv.reader(CsvFile)
			Data = []
			for rows in Reader:
				if rows:
					Data.append(rows[0].strip())
		return Data
	
	def _FindCsv(self, CsvFileName) -> str:
		"""
		Function dedicated to fetching the file named by user in argv[1].

		:Parameter: `CsvFileName` file to be searched for.

		:Returns: `CsvFilePath` a string containing the absolute path to the file.
		"""
		try:
			path = os.path.dirname(__file__)
			path = os.path.dirname(path)
			path = os.path.dirname(path)
			CsvFileName = os.path.abspath(f'{CsvFileName}')
			CsvFilePath = os.path.join(path, f'{CsvFileName}')
		except Exception as e:
			exit(print(f'{CsvFileName}: {e}'))
		return CsvFilePath
	
	def _SingleEntry(self, Domain) -> None:
		self._Entries = [Domain]


## OLD STUFF

				# try:
				# 	async with session.get(f'https://{domain}') as response:
				# 		if response.status == 200:
				# 			html = await response.text()
				# 			if RobotsNotAllowed is True:
				# 				conn.execute('''
				# 					INSERT OR REPLACE INTO domains (
				# 						domain, html_body, robots_txt, fetch_status
				# 	 				) VALUES (?, ?, ?, ?)
				# 				''', (domain, html, 0, response.status))
				# 				SuccessCounter += 1
				# 				print(f"☑️ {domain}: Success, but robots.txt was present in domain")
				# 			else:
				# 				conn.execute('''
				# 					INSERT OR REPLACE INTO domains (
				# 						domain, html_body, robots_txt, fetch_status
				# 					) VALUES (?, ?, ?, ?)
				# 				''', (domain, html, 1, response.status))
				# 				SuccessCounter += 1
				# 				print(f"✅ {domain}: Success")
				# 		else:
				# 			conn.execute('''
				# 				INSERT OR REPLACE INTO domains (
				# 					domain, fetch_status
				# 				) VALUES (?, ?)
				# 			''', (domain, response.status))
				# 			FailedCounter += 1
				# 			print(f"⚠️  {domain}: HTTP {response.status}")
							
				# except aiohttp.ClientResponseError as e:
				# 	conn.execute('''
				# 		INSERT OR REPLACE INTO domains (
				# 			domain, fetch_status
				# 		) VALUES (?, ?)
				# 	''', (domain, e.status if hasattr(e, 'status') else 0))
				# 	OtherErrorCounter += 1
				# 	print(f"❌ {domain}: HTTP Error {e.status}")
					
				# except Exception as e:
				# 	conn.execute('''
				# 		INSERT OR REPLACE INTO domains (
				# 			domain, fetch_status
				# 		) VALUES (?, ?)
				# 	''', (domain, 0))
				# 	OtherErrorCounter += 1
				# 	print(f"❌ {domain}: {type(e).__name__}: {e}")