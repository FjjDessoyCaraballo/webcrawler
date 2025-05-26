import os
import csv
import sqlite3

class Fetcher:
	def __init__(self):
		self._conn = []
		return
	
	def EntryPoint(self, DbPath: str) -> bool:
		if DbPath == '':
			exit(print('Error: database not found'))
		self._conn = sqlite3.connect(DbPath)
		print('Executed to the end')
		self._conn.close()
		return True