import os
import sqlite3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import glob

def Cherrypicker():
	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	df = pd.read_csv(LatestCsv)
	sample = df[['domain', 'logo_url']].dropna().sample(5)
	for _, row in sample.iterrows():
		print(f"{row['domain']}: {row['logo_url']}")

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
	plt.title('robots.txt: Are robots allowed?\n(0 not allowed / 1 allowed)', fontsize=16, fontweight='bold')
	labels = [f'{key}\n{value} ({value/sum(data.values())*100:.1f}%)' for key, value in data.items()]
	plt.pie(data.values(), labels=labels)
	plt.show()
	conn.close()

def BandsOfConfidenceBar():
	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	df: pd.DataFrame = pd.read_csv(LatestCsv)

	bins = [0.0, 0.2, 0.5, 0.7, 0.9, 1.0]
	labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
	
	df['confidence_band'] = pd.cut(df['confidence_score'], bins=bins, labels=labels, include_lowest=True)

	BandCounts = df['confidence_band'].value_counts().sort_index()
	BandCounts.plot.bar()	
	plt.title('Distribution of Confidence Score Bands', fontsize=16, fontweight='bold')
	plt.xlabel('Confidence Bands')
	plt.ylabel('Count')
	plt.xticks(rotation=15)
	plt.show()

def BandsOfConfidencePerc():
	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	df = pd.read_csv(LatestCsv)

	bins = [0.0, 0.2, 0.5, 0.7, 0.9, 1.0]
	labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

	df['confidence_band'] = pd.cut(df['confidence_score'], bins=bins, labels=labels, include_lowest=True)
	BandCounts = df['confidence_band'].value_counts().sort_index()

	# Pie chart with percentages AND counts
	total = BandCounts.sum()
	BandCounts.plot.pie(autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100*total)})')
	plt.title('Distribution of Confidence Score Bands')
	plt.show()


def Visualizer():
	FetchedVsNonfetched()
	RobotsPresent()
	BandsOfConfidencePerc()
	BandsOfConfidenceBar()
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