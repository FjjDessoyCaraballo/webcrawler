import os
import csv

class Crawler:
	def __init__(self):
		self._File: list[dict[str, str]] = []

	def EntryPoint(self, domains, mode):
		if mode == 1:
			self.CsvEntry(domains)
		elif mode == 2:
			self.SingleEntry(domains)
		return

	def CsvEntry(self, domains):
		path = self.FindCsv(domains)
		self._File = self.OpenCsv(path)
		print(f'{self._File}')
		return
	
	def OpenCsv(self, CsvPath) -> list[dict[str, str]]:
		with open(CsvPath, 'r') as CsvFile:
			Reader = csv.DictReader(CsvFile)
			Data = list(Reader)
		return Data
	
	def FindCsv(self, CsvFileName) -> str:
		path = os.path.dirname(__file__)
		path = os.path.dirname(path)
		path = os.path.dirname(path)
		CsvFileName = os.path.abspath(f'{CsvFileName}')
		CsvFilePath = os.path.join(path, f'{CsvFileName}')
		if CsvFilePath is None:
			exit(print(f'{CsvFileName} does not exist in the repository.'))
		return CsvFilePath
	
	def SingleEntry(self, domain):
		print("we found a single entry")
		return