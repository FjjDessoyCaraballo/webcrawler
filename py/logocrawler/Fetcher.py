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
		LogoUrl = self._SVGMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'SVG_TAG')
			return True

		# Method 2: img tags
		LogoUrl = self._IMGMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'IMG_TAG')
			return True
		
		# Method 3: custom tags
		LogoUrl = self._CustomTagMethod(HtmlBody, Domain)
		if LogoUrl is not None:
			self._InsertLogoIntoDb(RowId, LogoUrl, 'CUSTOM_TAG')
			return True

		return False

	async def _SVGMethod(self, HtmlBody: str, Domain: str):
		"""
		Method #1 for logo extraction by converting SVG into URL data methodology using base64.

		:Parameter: HtmlBody string of the index.html of given domain in database.
		
		:Parameter: Domain string containing the landing page/homepage of given domain.

		:Returns: LogoUrl string containing URL of logo image. Returns None if method fails to find logo.
		"""
		LogoUrl: str = ''
		return None

	async def _IMGMethod(self, HtmlBody: str, Domain: str):
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

	async def _InsertLogoIntoDb(self, RowId: int, LogoUrl: str, Method: str) -> None:
		"""
		Method that exclusively deals with inserting logos into the database.

		:Parameter: RowId integer representing which row of the database the HTML body is from.
		
		:Parameter: LogoUrl URL that contains logo image.
		
		:Parameter: Method methodology used to obtain logo.
		
		:Returns: None
		"""
		self._conn.execute(''''
					UPDATE domains
					SET logo_url = ?, extraction_method = ?
					WHERE id = ?
					''', (LogoUrl, Method, RowId))

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
