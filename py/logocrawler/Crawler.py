import os
import csv
from typing import TypedDict
import aiohttp
import asyncio
import sqlite3

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

	async def _StoreRequests(self) -> None:
		"""
		Fetch the index.html file from all listed domains and insert them into the database.
		"""
		conn = sqlite3.connect(self._DbPath)

		async with aiohttp.ClientSession() as session:
			for domain in self._Entries:
				try:
					async with session.get(f'https://{domain}') as response:
						if session.status == 200:
							html = await response.text()
							conn.execute('''
								INSERT OR REPLACE INTO domains (
									domain, html_body, fetch_status
								) VALUE (?, ?, ?)
							''', (domain, html, response.status))
						else:
							conn.execute('''
								INSERT OR REPLACE INTO domains (
									domain, fetch_status
								) VALUE (?, ?)
							''', (domain, response.status))
				except Exception as e:
					exit(print(f'Error fetching {domain}: {e}'))
					conn.execute('''
								INSERT OR REPLACE INTO domains (
				  					domain, fetch_status
				  				) VALUE (?, ?)
							''', (domain, 0))
		conn.commit()
		conn.close()

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