
from webbrowser import Error

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import requests
import re
import pandas as pd
from selenium.webdriver.support.wait import WebDriverWait
import csv

def get_info(query):

    # Fetch the search results page from Yahoo Finance
    search_url = f"https://www.alphaquery.com/stock/{query}/profile-key-metrics"
    print(search_url)
    soup = BeautifulSoup(requests.get(search_url).content, 'html.parser')

    html_list_financial = soup.find_all('div', class_="col-lg-6")
    html_list_stocks = soup.find('div', class_="col-lg-4 col-md-12 margin-top-rem")

    html_list = str(html_list_financial).split('\n')

    html_list_stock = str(html_list_stocks).split('\n')

    data_finance = []
    data_stock = []

    for index, html in enumerate(html_list):
        if html == "<tr>":
            data_finance.append((html_list[index+1],html_list[index+2]))

    for index, data in enumerate(html_list_stock):
        if data == "<tr>":
            data_stock.append((html_list_stock[index+1],html_list_stock[index+2]))


    return data_finance, data_stock

def get_ticker(company_name):

    # Replace spaces in the company name with '+' for the search query
    search_query = company_name.replace(" ", "+")

    # Fetch the search results page from Yahoo Finance
    search_url = f"https://finance.yahoo.com/lookup?s={search_query}"

    driver = webdriver.Firefox()

    pattern = re.compile(re.escape(search_query), re.IGNORECASE)

    try:
        driver.get(search_url)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a")))
        print(f"Query: {search_query}")
        print(f"Search URL: {search_url}")

        # Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ticker_tags = soup.find('a', class_="loud-link fin-size-medium yf-1e4diqp")
        words = str(ticker_tags).split(' ')
        word = words[len(words)-2]
        ticker = ''
        for index, char in enumerate(word):
            if(char == '>'):
                ticker = word[index+1:]
                break
        return ticker
    except Error as e:
        return "Ticker not found"

def save_to_csv(data_qual, data_quan, filename='data/financials.csv'):
    # Combine qualitative and quantitative data
    combined_data = list(zip(data_qual, data_quan))

    # Write data to a CSV file
    with open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['Qualitative', 'Quantitative'])
        # Write the rows
        writer.writerows(combined_data)

    print(f"Data saved to {filename}")

if __name__ == '__main__':
    data_finance, data_stock = get_info(get_ticker('facebook'))

    data_qual = []
    data_quan = []
    data_stk = []

    data_temp = [('<td>Exchange</td>', '<td>NASDAQ</td>'), ('<td>Sector</td>', '<td>Communication Services</td>'), ('<td>Industry</td>', '<td>Internet Content &amp; Information</td>'), ('<td>Common Shares Outstanding</td>', '<td class="indicator-figure">2.52B</td>'), ('<td>Free Float</td>', '<td class="indicator-figure">2.18B</td>'), ('<td>Market Capitalization</td>', '<td class="indicator-figure">$1476.37B</td>'), ('<td>Average Volume (Last 20 Days)</td>', '<td class="indicator-figure">13.04M</td>'), ('<td>Beta (Past 60 Months)</td>', '<td class="indicator-figure">1.22</td>'), ('<td>Percentage Held By Insiders (Latest Annual Proxy Report)</td>', '<td class="indicator-figure">13.71%</td>'), ('<td>Percentage Held By Institutions (Latest 13F Reports)</td>', '<td class="indicator-figure">79.91%</td>'), ('<td>Annual Dividend (Based on Last Quarter)</td>', '<td class="indicator-figure">$2.00</td>'), ('<td>Dividend Yield (Based on Last Quarter)</td>', '<td class="indicator-figure">0.34%</td>')]


    for data in data_finance:
        data_qual.append(data[0].split('<td>')[1].split('</td>')[0])
        data_quan.append(data[1].split('>')[1].split('<')[0])

#    for data in data_stock:
#        print(data[0], '\n', data[1])

    for data in data_temp:
        try:
            data_qual.append(data[0].split('<td>')[1].split('</td>')[0])
        except IndexError:
            data_qual.append("Qualitative data not found")
        if data[1].startswith('<td class='):
            data_quan.append(data[1].split('>')[1].split('<')[0])
        else:
            data_quan.append(data[1].split('<td>')[1].split('</td>')[0])

    # save found data to csv
    save_to_csv(data_qual, data_quan)

    print(data_quan)
    print(data_qual)
