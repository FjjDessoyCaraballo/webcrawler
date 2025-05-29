import sqlite3
import os
import csv
import random
import glob

"""
I wanted to use pytest, but given the task I was given it would've taken far too much
time to write proper unit tests with assertion testing. Therefore I wrote down tests
derived from the created database.

NB: The database is not present in the repository since it is quite hefty (almost 200mb)
for the regular git repository.
"""

def TestDatabaseContent(db_path):
	"""
	Check what's in the database
	"""
	if not os.path.exists(db_path):
		print(f"Database not found at {db_path}")
		return False
	
	conn = sqlite3.connect(db_path)
	cursor = conn.cursor()
	
	cursor.execute("SELECT COUNT(*) FROM domains")
	total = cursor.fetchone()[0]
	print(f"Total domains in database: {total}")
	
	cursor.execute("SELECT COUNT(*) FROM domains WHERE fetch_status = 200")
	successful = cursor.fetchone()[0]
	print(f"Successfully fetched domains: {successful}")
	
	cursor.execute("SELECT COUNT(*) FROM domains WHERE logo_url IS NOT NULL")
	with_logos = cursor.fetchone()[0]
	print(f"Domains with logos already extracted: {with_logos}")
	
	print("\nSample domains (first 5 with HTML):")
	cursor.execute("""
		SELECT domain, final_url, LENGTH(html_body) as html_size 
		FROM domains 
		WHERE fetch_status = 200 AND html_body IS NOT NULL
		LIMIT 5
	""")
	for row in cursor.fetchall():
		print(f"  - {row[0]} -> {row[1]} (HTML size: {row[2]} bytes)")
	
	conn.close()
	return True

def TestSpecificDomain(DbPath, Domain):
	"""
	Test extraction for a specific domain
	"""
	conn = sqlite3.connect(DbPath)
	cursor = conn.cursor()
	
	cursor.execute("""
		SELECT id, html_body, final_url 
		FROM domains 
		WHERE domain = ? AND fetch_status = 200
	""", (Domain,))
	
	result = cursor.fetchone()
	if not result:
		print(f"Domain {Domain} not found or not successfully fetched")
		conn.close()
		return
	
	RowId, HtmlBody, FinalUrl = result
	print(f"\nTesting {Domain} (ID: {RowId}):")
	print(f"Final URL: {FinalUrl}")
	print(f"HTML size: {len(HtmlBody)} bytes")
	
	HtmlLower = HtmlBody.lower()
	indicators = {
		'SVG tags': HtmlLower.count('<svg'),
		'IMG tags': HtmlLower.count('<img'),
		'Logo mentions': HtmlLower.count('logo'),
		'Brand mentions': HtmlLower.count('brand'),
		'Favicon links': HtmlLower.count('rel="icon"') + HtmlLower.count("rel='icon'")
	}
	
	print("\nHTML indicators found:")
	for indicator, count in indicators.items():
		if count > 0:
			print(f"  - {indicator}: {count}")
	
	conn.close()

def main():
	DbPath = '../logos.db'
	
	print(f"Testing Fetcher with database: {DbPath}\n")
	
	if not TestDatabaseContent(DbPath):
		return 1

	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	print("\n" + "="*50)
	print(f'Latest csv: {LatestCsv}')
	with open(LatestCsv) as CsvFile:
		Reader = csv.reader(CsvFile)
		Data = []
		for rows in Reader:
			if rows:
				Data.append(rows[0].strip())
	
	Sample = random.sample(Data, 5)

	TestDomains = Sample
	for domain in TestDomains:
		TestSpecificDomain(DbPath, domain)
		print("\n" + "="*50)

	
	print("\n" + "="*50)
	print("To run the full Fetcher, use:")
	print(f"  ./fetch.sh")
	print("="*50)
	
	return 0

if __name__ == "__main__":
	main()