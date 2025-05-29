import os
import sqlite3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import glob

def Cherrypicker():

	return

def FetchedVsNonfetched():
	conn = sqlite3.connect('../logos.db')
	data = dict(conn.execute('SELECT fetch_status, COUNT(*) FROM domains GROUP BY fetch_status').fetchall())
	plt.title('Distribution of Fetch Status Codes\nLogo Crawler Results', fontsize=16, fontweight='bold')
	plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%')
	plt.show()
	conn.close()

def RobotsPresent():
	conn = sqlite3.connect('../logos.db')
	data = dict(conn.execute('SELECT robots_txt, COUNT(*) FROM domains WHERE fetch_status = 200 GROUP BY robots_txt').fetchall())
	plt.title('Presence of robots_txt\n(1 for present / 0 for not present)', fontsize=16, fontweight='bold')
	labels = [f'{key}\n{value} ({value/sum(data.values())*100:.1f}%)' for key, value in data.items()]
	plt.pie(data.values(), labels=labels)
	plt.show()
	conn.close()
def Visualizer():
	FetchedVsNonfetched()
	RobotsPresent()
	
	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	df: pd.DataFrame = pd.read_csv(LatestCsv)

	return

def main():
	## ASSUME THAT THIS IS RAN AT ROOT OF DIRETORY
	if len(sys.argv) == 2:
		if sys.argv[1] == 'vizz':
			Visualizer()
		elif sys.argv[1] == 'cherrypick':
			Cherrypicker()
		else:
			print('Whoopsie')
			return 1
	else:
		return 1
	return 0

if __name__ == "__main__":
	main()