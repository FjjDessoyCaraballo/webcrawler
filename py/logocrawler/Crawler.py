import os
import csv
import sqlite3
import aiohttp
import asyncio

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
			   logo_url TEXT,
			   favicon_url TEXT,
			   fetch_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
			   fetch_status INTEGER,
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
		OtherErrorCounter: int = 0

		conn = sqlite3.connect(self._DbPath)

		connector = aiohttp.TCPConnector(
			limit=100,
			limit_per_host=1,
			ttl_dns_cache=300
		)
		
		timeout = aiohttp.ClientTimeout(total=15)
		
		async with aiohttp.ClientSession(
			connector=connector,
			timeout=timeout,
			headers={'User-Agent': 'Mozilla/5.0 (compatible; LogoCrawler/1.0)'},
			# Got some help from AI here to define limits in the response
			read_bufsize=65536,  # 64KB read buffer
			max_line_size=16384,  # 16KB max line size
			max_field_size=16384  # 16KB max header field size
		) as session:
			for domain in self._Entries:
				RobotsNotAllowed = await self._CheckRobotsTxt(session, domain)

				try:
					async with session.get(f'https://{domain}') as response:
						if response.status == 200:
							html = await response.text()
							if RobotsNotAllowed is True:
								conn.execute('''
									INSERT OR REPLACE INTO domains (
										domain, html_body, robots_txt, fetch_status
					 				) VALUES (?, ?, ?, ?)
								''', (domain, html, 0, response.status))
								SuccessCounter += 1
								print(f"☑️ {domain}: Success, but robots.txt was present in domain")
							else:
								conn.execute('''
									INSERT OR REPLACE INTO domains (
										domain, html_body, robots_txt, fetch_status
									) VALUES (?, ?, ?, ?)
								''', (domain, html, 1, response.status))
								SuccessCounter += 1
								print(f"✅ {domain}: Success")
						else:
							conn.execute('''
								INSERT OR REPLACE INTO domains (
									domain, fetch_status
								) VALUES (?, ?)
							''', (domain, response.status))
							FailedCounter += 1
							print(f"⚠️  {domain}: HTTP {response.status}")
							
				except aiohttp.ClientResponseError as e:
					conn.execute('''
						INSERT OR REPLACE INTO domains (
							domain, fetch_status
						) VALUES (?, ?)
					''', (domain, e.status if hasattr(e, 'status') else 0))
					OtherErrorCounter += 1
					print(f"❌ {domain}: HTTP Error {e.status}")
					
				except Exception as e:
					conn.execute('''
						INSERT OR REPLACE INTO domains (
							domain, fetch_status
						) VALUES (?, ?)
					''', (domain, 0))
					OtherErrorCounter += 1
					print(f"❌ {domain}: {type(e).__name__}: {e}")
		
		conn.commit()
		conn.close()
		print(f"\nCompleted fetching {len(self._Entries)} domains")
		print(f"\n✅Successfully fetched: {SuccessCounter}")
		print(f"\n⚠️Failed to fetch: {FailedCounter}")
		print(f"\n❌ Other errors: {OtherErrorCounter}")

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