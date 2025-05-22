import Crawler as crawler
import sys

def main():
	CrawlerInstance = crawler.Crawler()
	domain: str = ''
	if len(sys.argv) == 2:
		CrawlerInstance.EntryPoint(sys.argv[1], 1)
	else:
		domain = input("Provide a domain: ")
		if domain == '':
			return 
		CrawlerInstance.EntryPoint(domain, 2)
	return

if __name__ == "__main__":
	main() 
	