import os
import sqlite3
import sys
import pandas as pd
import matplotlib.pyplot as plt
import glob

def Cherrypicker():
	LatestCsv = max(glob.glob("data/websites_logos_*.csv"))
	df = pd.read_csv(LatestCsv)

	df_with_logos = df[['domain', 'logo_url', 'confidence_score']].dropna()

	if df_with_logos.empty:
		print("No domains with logos and confidence scores found.")
		return

	bins = [0.0, 0.2, 0.5, 0.7, 0.9, 1.0]
	labels = ['Very Low (0.0-0.2)', 'Low (0.21-0.5)', 'Medium (0.51-0.7)', 
	          'High (0.71-0.9)', 'Very High (0.91-1.0)']

	df_with_logos['confidence_band'] = pd.cut(df_with_logos['confidence_score'], 
	                                          bins=bins, labels=labels, include_lowest=True)

	grouped = df_with_logos.groupby('confidence_band', observed=True)
	band_counts = df_with_logos['confidence_band'].value_counts().sort_index()

	print("🎯 Logo Extraction Results by Confidence Level")
	print("=" * 60)
	print(f"Total domains with extracted logos: {len(df_with_logos)}")
	print()

	print("Available confidence bands:")
	band_options = {}
	option_num = 1

	for band in reversed(labels):
		count = band_counts.get(band, 0)
		if count > 0:
			print(f"  {option_num}. {band} ({count} domains)")
			band_options[str(option_num)] = band
			option_num += 1

	print(f"  {option_num}. All bands (overview)")
	band_options[str(option_num)] = "all"
	print("  0. Exit")
	print()

	# User selection
	while True:
		choice = input("Enter your choice (number): ").strip()

		if choice == "0":
			print("Goodbye!")
			return
		elif choice in band_options:
			selected_band = band_options[choice]
			break
		else:
			print("Invalid choice. Please try again.")

	print("\n" + "=" * 60)

	if selected_band == "all":
		print("📊 Overview of All Confidence Bands")
		print("-" * 40)
		for band in reversed(labels):
			count = band_counts.get(band, 0)
			percentage = (count / len(df_with_logos)) * 100 if count > 0 else 0
			print(f"  {band}: {count} domains ({percentage:.1f}%)")
		print()

		for band in reversed(labels):
			if band in grouped.groups:
				band_data = grouped.get_group(band)
				sample = band_data.sample(1)
				row = sample.iloc[0]

				logo_url = row['logo_url']

				print(f"🌐 {row['domain']} ({band.split('(')[0].strip()})")
				print(f"   Score: {row['confidence_score']:.3f} | Logo: {logo_url}")
	else:
		band_data = grouped.get_group(selected_band)
		print(f"📊 {selected_band} Confidence Band")
		print(f"📈 {len(band_data)} domains in this band")
		print("-" * 40)

		max_examples = len(band_data)
		while True:
			try:
				num_examples = input(f"How many examples to show? (1-{max_examples}, or 'all'): ").strip()
				if num_examples.lower() == 'all':
					num_examples = max_examples
					break
				num_examples = int(num_examples)
				if 1 <= num_examples <= max_examples:
					break
				else:
					print(f"Please enter a number between 1 and {max_examples}")
			except ValueError:
				print("Please enter a valid number or 'all'")

		if num_examples == max_examples:
			sample = band_data.sort_values('confidence_score', ascending=False)
		else:
			sample = band_data.sample(num_examples)

		for i, (_, row) in enumerate(sample.iterrows(), 1):
			logo_url = row['logo_url']

			print(f"\n{i}. 🌐 {row['domain']}")
			print(f"   Score: {row['confidence_score']:.3f}")
			print(f"   Logo: {logo_url}")

	print("\n" + "=" * 60)

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