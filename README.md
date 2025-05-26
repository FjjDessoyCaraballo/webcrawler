# Introduction

This is a technical assignment where I'm building a web crawler to fetch logos from a diverse list of domains. The stack is mostly python.

## How to use

### Running on nix environment

This project is supposed to function in Nix virtual environment. If you do not have Nix installed, run the following line (if your package manager is `apt`, otherwise subsitute it for your package manager)

```bash
apt install nix-setup-systemd
```

Then run the following line

```bash
nix-shell
```

Inside the Nix virtual environment you can first check if the installation was successful by checking the Python versions

```bash
python --version
ipython --version
```

### Running Crawler

After that, inside the `py` directory you will find find another directory called `logocrawler`, inside of it you will find the script. 

> [!NOTE]
> For crawling, this program can work in two ways:
>
> 1) User provides a `csv` file or;
> 2) User provides an individual domain.

If you want to run a csv with a list of domains for the crawler to fetch, run the following line:

```bash
./crawl.sh
```

Or go into `py/logocrawler` and run the `Entry.py` file providing the path to the CSV file that contains the domains.

```bash
python Entry.py <csv-file> crawl
```

You can make manual entries by giving the `Entry.py` only one argument:

```bash
python Entry.py <domain>
```

### Running Fetcher

> [!CAUTION]
> The `Fetcher` only works if the crawler has ran at least once!
> Make sure to run the `Crawler` first and then run the `Fetcher` if this is your first time or you do not have a `logos.db`.

## Disclaimer

This project was designed for educational purposes only. When using Crawler or any other webcrawling methods, obey web etiquette of complying to `Robots.txt`.

(under construction)
