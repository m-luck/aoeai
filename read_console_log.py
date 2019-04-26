import time
from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome(executable_path='C:/chromedriver.exe')

driver.get('file:///C:/aoeai/SR/browserTest.html')

# print console log messages

while True:
    time.sleep(1) 
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    evolving = soup.find(id="evolving_value")
    print(evolving)

