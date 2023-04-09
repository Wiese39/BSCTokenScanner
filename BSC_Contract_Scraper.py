from undetected_chromedriver import Chrome
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re


def unique(file):
    with open(f"{file}.txt", "r") as f:
        addresses = f.read().splitlines()
        addresses = list(dict.fromkeys(addresses))
        with open("addresses.txt", "w") as f:
            for address in addresses:
                f.write(address + "\n")

start = 0
page = 1
count = 0
keyword = 'tokens/label'
links = []

def get_links(url, keywords):
    driver.get(url) # Navigate to the page
    while "Ray ID:" in driver.page_source:
        # Wait for 7 seconds to allow Cloudflare to verify the request
        time.sleep(0.3)
    time.sleep(1.3) # Wait for the page to load
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    response = soup.find_all('a')
    for a in response:
        for keyword in keywords:
            if keyword in a['href']:
                links.append(a['href'])
    with open("links.txt", "w") as f:
        for link in links:
            f.write(link + "\n")

def scrape_contracts(url, add_url, output_file):
    #strip "labelcloud" from the url
    url = url.split("/labelcloud")[0]
    driver.get(f"{url}/login")
    while "Ray ID:" in driver.page_source:
        # Wait for 7 seconds to allow Cloudflare to verify the request
        time.sleep(0.3) # Navigate to the login page
    time.sleep(20) # Wait for the page to load and for user to complete captcha
    with open("links.txt", "r") as f:
        links = f.read().splitlines()
        for link in links:
            count = 0
            start = 0
            page = 1
            URL = link + add_url
            while True:
                driver.get(URL) # Navigate to the page
                print("Scraping url " + URL)
                while "Ray ID:" in driver.page_source:
                    # Wait for 7 seconds to allow Cloudflare to verify the request
                    time.sleep(0.3)
                time.sleep(1.3) # Wait for the page to load
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                response = soup.find_all('td')
                td_regex = r"<td[^>]*>(.*?)<\/td>"
                td_matches = re.findall(td_regex, str(response))
                for td in td_matches:
                    if "Contract" in td:
                        match = re.search(r'href="([^"]+)"', td)
                        if match:
                            href = match.group(1)
                            address = href.split("/address/")[1]
                            with open(f"{output_file}.txt", "a") as f:
                                f.write(address + "\n")
                                count += 1
                if "tokens" in URL:
                    #find all href in the page
                    hrefs = re.findall(r'href="([^"]+)"', str(response))
                    for href in hrefs:
                        if "address" in href:
                            address = href.split("/address/")[1]
                            with open(f"{output_file}.txt", "a") as f:
                                f.write(address + "\n")
                                count += 1
                #if this page is loaded https://bscscan.com/error then break
                if "error" in driver.current_url:
                    print("Scraped " + str(count) + " addresses on " + str(page) + " pages.")
                    if page > 1:
                        page -= 1
                    break
                start += 50
                page += 1
                #replace start= with start={start}
                URL = URL.replace(f"start={start-50}", f"start={start}")

    with open(f"{output_file}.txt", "r") as f:
        addresses = f.read().splitlines()
        print("Total number of addresses: " + str(len(addresses))) 
    driver.quit() # Close the browser window when done

if __name__ == "__main__":
    driver = Chrome() # Replace with path to your chromedriver executable
    #use subprocess
    add_url = "?subcatid=undefined&size=50&start=0&col=3&order=desc"
    chain = input("Enter the name of the chain you want to scrape (e.g. bsc, ether, polygonscan, avax): ")
    links = input("Extract links from the labelcloud page? (y/n): ")
    file = input("Enter the name of the output file: ")
    linkgetter = False
    keyword = []
    if links == "y":
        linkgetter = True
    if linkgetter:
        if not chain == "avax":
            url = f"https://{chain}scan.com/labelcloud"
            get_links(url, keyword)
        else:
            url = f"https://snowtrace.io/labelcloud"
            get_links(url, keyword)
    if not chain == "avax":
        url = f"https://{chain}scan.com/labelcloud"
        scrape_contracts(url, add_url, chain)
    else:
        url = f"https://snowtrace.io/labelcloud"
        scrape_contracts(url, add_url, chain)
    unique(file)
