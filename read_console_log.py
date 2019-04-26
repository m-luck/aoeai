from selenium import webdriver
import time

driver = webdriver.Chrome(executable_path='C:/chromedriver.exe')

driver.get('file:///C:/aoeai/SR/browserTest.html')

# print console log messages

while True:
    time.sleep(1) 
    for entry in driver.get_log('browser'):
        print(entry)
