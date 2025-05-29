import os
import sys
import pandas

def Cherrypicker():

	return

def Visualizer():
	
	return

def main():
	if len(sys.argv == 2):
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