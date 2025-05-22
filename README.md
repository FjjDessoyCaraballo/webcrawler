# Introduction

This is a technical assignment where I'm building a web crawler to fetch logos from a diverse list of domains. The stack is mostly python.

## How to use

This project is supposed to function in Nix virtual environment. If you do not have Nix installed, run the following line (if your package manager is `apt`, otherwise subsitute it for your package manager)

```bash
apt install nix-setup-systemd
```

Then run the following line

```bash
$ nix-shell
```

Inside the Nix virtual environment you can first check if the installation was successful by checking the Python versions

```bash
python --version
ipython --version
```

After that, inside the `py` directory you will find find another directory called `logocrawler`, inside of it you will find the script. 

**ATTENTION!!!** this program can work in two ways: 1) User provides a `csv` file or; 2) User provides an individual domain.

If you want to run a csv with a list of domains for the crawler to fetch, run the following line:

```bash
$ python3 Entry.py your_file.csv
```

Or just run the `Entry.py` file without arguments

```bash
$ python Entry.py
```

(under construction)