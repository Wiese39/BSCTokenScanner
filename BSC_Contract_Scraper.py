from undetected_chromedriver import Chrome
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import re


def unique():
    with open("addresses.txt", "r") as f:
        addresses = f.read().splitlines()
        addresses = list(dict.fromkeys(addresses))
        with open("addresses.txt", "w") as f:
            for address in addresses:
                f.write(address + "\n")
# unique()
# exit()

driver = Chrome() # Replace with path to your chromedriver executable
#use subprocess
driver.get('https://etherscan.com/login') # Navigate to the login page
time.sleep(20) # Wait for the page to load and for user to complete captcha

#auto login
# driver.find_element_by_id("login").send_keys("wiese222")
# driver.find_element_by_id("password").send_keys("Hallo123!")
# driver.find_element_by_id("loginbtn").click()
# time.sleep(5)
add_url = "?subcatid=undefined&size=50&start=0&col=3&order=desc"
start = 0
page = 1
count = 0
url = 'https://etherscan.com/labelcloud'
keyword = 'tokens/label'
links = []

# # Load the page
# driver.get(url)

# # Find all links that contain the keyword
# elements = driver.find_elements(By.XPATH, f"//a[contains(@href, '{keyword}')]")

# # Extract the links from the elements
# links = [element.get_attribute('href') for element in elements]
# #append all links to file
# with open("links.txt", "a") as f:
#     for link in links:
#         f.write(link + "\n")

#loop through all links from file
with open("links.txt", "r") as f:
    links = f.read().splitlines()
    for link in links:
        URL = link + add_url
        print("Scraping url " + URL)
        driver.get(URL) # Navigate to the page
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
                    with open("addresses.txt", "a") as f:
                        f.write(address + "\n")
                        count += 1
        
        #if this page is loaded https://bscscan.com/error then break
        if "error" in driver.current_url:
            print("Scraped " + str(count) + " addresses on " + str(page) + " pages.")
            if page > 1:
                page -= 1
            continue
        start += 50
        page += 1
        #replace start= with start={start}
        URL = URL.replace(f"start={start-50}", f"start={start}")

with open("addresses.txt", "r") as f:
    addresses = f.read().splitlines()
    print("Total number of addresses: " + str(len(addresses))) 
driver.quit() # Close the browser window when done




