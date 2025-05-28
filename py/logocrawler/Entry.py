import Crawler as crawler
import Fetcher as fetcher
import sys

def main():
	
	if len(sys.argv) == 3 and sys.argv[2] == 'crawl':
		# regular crawling bot operation where he looks for domains in csv
		CrawlerInstance = crawler.Crawler()
		domain: str = ''
		CrawlerInstance.EntryPoint(sys.argv[1], 1)
	elif len(sys.argv) == 2:
		# manual input of individual domains. Who knows
		domain = input("Provide a domain: ")
		if domain == '':
			return 1
		CrawlerInstance.EntryPoint(domain, 2)
	elif len(sys.argv) == 3 and sys.argv[2] == 'fetch':
		# fetcher works with pre-existing db generated from crawler
		FetcherInstance = fetcher.Fetcher()
		FetcherInstance.EntryPoint(sys.argv[1])

	return 0

if __name__ == "__main__":
	main() 
	