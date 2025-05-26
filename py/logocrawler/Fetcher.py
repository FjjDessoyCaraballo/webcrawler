import os
import csv
import sqlite3

class Fetcher:
	def __init__(self):
		self._DbPath = 'logos.db'