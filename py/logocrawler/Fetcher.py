import os
import csv
import sqlite3
from typing import Optional, Tuple, List, Union

class Fetcher:
	def __init__(self):
		self._conn: sqlite3.Connection = []
		self._rows = ()
		return
	
	def EntryPoint(self, DbPath: str) -> bool:
		if DbPath == '':
			exit(print('Error: database not found'))
		self._conn = sqlite3.connect(DbPath)
		Cursor = self._FetchRows()
		self._ProcessRows(Cursor)
		print('Executed to the end')
		self._conn.close()
		return True
	
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
		row: Tuple[int, str, str, str]
		for row in Cursor:
			RowId, Domain, HtmlBody, FinalUrl = row
			print(f'[{RowId}] 🔵 Attemping to extract logo for {Domain}')
			self._ScanHtml(HtmlBody)
			break
		return
	
	def _ScanHtml(self, RowId: int, HtmlBody: str):
		"""
		Method to scan the HTML and find which method we are using to extract the logo.
		"""
		print(HtmlBody)
		return

	def _InsertLogoIntoDb(self, RowId: int, LogoUrl: str, Method: str) -> None:
		return

	# fetch a row from a domain that returned status code 200
	# make a function to go through the html file
	# find references to "logo"