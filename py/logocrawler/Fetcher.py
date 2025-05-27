import os
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
		except Exception as e:
			print(f'Error: {e}')
			return False
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
	
	async def _ProcessRows(self, Cursor: sqlite3.Cursor):
		row: Tuple[int, str, str, str]
		for row in Cursor:
			RowId, Domain, HtmlBody, FinalUrl = row
			print(f'[{RowId}] 🔵 Attemping to extract logo for {Domain}')
			self._ScanHtml(HtmlBody)

	async def _ScanHtml(self, RowId: int, HtmlBody: str) -> str:
		"""
		Method to scan the HTML and find which method we are using to extract the logo.
		"""
		LogoUrl: str

		# Method 1: SVG tags
		LogoUrl = self._SVGMethod()
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'SVG_TAG')
			return

		# Method 2: img tags
		LogoUrl = self._IMGMethod()
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'IMG_TAG')
			return
		
		# Method 3: custom tags
		LogoUrl = self._CustomTagMethod()
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'CUSTOM_TAG')
			return
		
		# favicon?

		return None

	async def _SVGMethod(self):
		return

	async def _IMGMethod(self):
		return

	async def _CustomTagMethod(self):
		return

	async def _InsertLogoIntoDb(self, RowId: int, LogoUrl: str, Method: str) -> None:
		return

	# fetch a row from a domain that returned status code 200
	# make a function to go through the html file
	# find references to "logo"