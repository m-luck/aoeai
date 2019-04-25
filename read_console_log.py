from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities    

capabilities = DesiredCapabilities.CHROME
capabilities['loggingPrefs'] = { 'browser':'ALL' }

driver = webdriver.Chrome(desired_capabilities=capabilities)

driver.get('http://foo.com')

# print console log messages
for entry in driver.get_log('browser'):
    print entry