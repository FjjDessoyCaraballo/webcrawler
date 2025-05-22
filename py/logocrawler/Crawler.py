import os
import csv
from typing import TypedDict
import aiohttp
import asyncio

class DomainRecord(TypedDict):
	"""
	Class to define what our list of dictionaries will contain. This is mostly for documentation reasons.
	"""
	domain: str
	logo_url: str
	favicon_url: str

class Crawler:
	def __init__(self):
		self._Entries: list[DomainRecord] = []

	def EntryPoint(self, Domains, mode):
		"""
		Entrypoint should be the only public function to avoid confusion. We will work
		with the bare minimum and work our way to the webscrapping after this.

		:Parameter: `Domains` If mode (1) is selected, domains contains a csv file, otherwise it is a single domain url.

		:Parameter: `mode` defines if we are working with a csv file (1) or single entry mode (2)

		:Returns: None
		"""
		SingleEntry = False
		if mode == 1:
			self.CsvEntry(Domains)
		elif mode == 2:
			SingleEntry = True
			self.SingleEntry(Domains)
		self.MakeRequests()

	async def MakeRequests(self):
		
		return 

	def CsvEntry(self, Domains):
		"""
		This function is called when mode (1) was chosen. We proceed to parse the csv file.
		Any user faulty input will make the program exit during parsing time.

		:Parameter: `Domains` csv file that contains a list of domains for logo extraction.

		:Returns: None
		"""
		try:
			path = self.FindCsv(Domains)
			self._Entries = self.OpenCsv(path)
		except Exception as e:
			print(f"Error: {e}")
		return
	
	def OpenCsv(self, CsvPath) -> list[DomainRecord]:
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
					DomainDictionary = {
						'domain': rows[0].strip(), 
						'logo_url': '',
						'favicon_url': ''
					}
					Data.append(DomainDictionary)
		return Data
	
	def FindCsv(self, CsvFileName) -> str:
		"""
		Function dedicated to fetching the file named by user in argv[1].

		:Parameter: `CsvFileName` file to be searched for.

		:Returns: `CsvFilePath` a string containing the absolute path to the file.
		"""
		path = os.path.dirname(__file__)
		path = os.path.dirname(path)
		path = os.path.dirname(path)
		CsvFileName = os.path.abspath(f'{CsvFileName}')
		CsvFilePath = os.path.join(path, f'{CsvFileName}')
		if CsvFilePath is None:
			exit(print(f'{CsvFileName} does not exist in the repository.'))
		return CsvFilePath
	
	def SingleEntry(self, Domain) -> None:
		Data = []
		SingleEntry = {
			'domain': Domain,
			'logo_url': '',
			'favicon_url': ''
		}
		Data.append(SingleEntry)
		self._Entries = Data