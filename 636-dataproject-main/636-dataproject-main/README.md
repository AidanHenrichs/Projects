# 636-dataproject

This project is designed to take retail sentiment from social media sources in conjunction with financial news along with company financials to deliver either a negative, positive or neutral earnings report.

> current design supports only `reddit` and `yahoo finance` additional sources can be integrated with some further engineering.

## directory

```sh
> .venv
> data
  > ...
  > .csv-files
> .. python scripts
```

## viewing and editing the package list

```sh
pip freeze # only works once in the python enviroment; fetches all packages/versions and prints them to console
```

## active scrapers
Reddit: WallStreeBets </br>
Beautiful Soup: Yahoo Finance </br>

## run it yourself

> must have python 3 or higher installed

```sh
python -m venv .venv; source ./.venv/bin/activate; pip install --upgrade pip; pip install -r requirements.txt
```

## clean up

```sh
deactivate       # exits python enviroment

rm -rf .venv     # deletes python enviroment
```
