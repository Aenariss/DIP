from selenium import webdriver
import selenium.webdriver.chrome.service as ChromeService
import time

custom_browser_path = "C:/Program Files/Avast Software/Browser/Application/AvastBrowser.exe"
profile = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data"


chromedriver_path = "./chromedriver_134.exe"

    # Browser options
options = webdriver.ChromeOptions()
options.binary_location = custom_browser_path
options.add_argument('user-data-dir=' + profile)
options.add_argument('--use-fake-device-for-media-stream')
options.page_load_strategy = 'normal'  # Explicitly setting it

options.add_argument('--ignore-certificate-errors')
options.add_argument('--no-default-browser-check')
options.add_argument('--enable-features=SidePanelProjectInternal')
options.add_experimental_option('prefs', {'side_panel.show_at_startup': True})


options.add_experimental_option('excludeSwitches', ['load-extension', 'enable-automation', 'test-type', 'disable-sync'])

# set Chrome service
service = ChromeService.Service(executable_path=chromedriver_path)

# set desired capabilities
options.set_capability('goog:loggingPrefs', {'browser': 'ALL', 'performance': 'ALL'})
options.set_capability('goog:perfLoggingPrefs', {'bufferUsageReportingInterval': 1000})

driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)

driver.get("https://seznam.cz")

print("Loaded")

time.sleep(100)
driver.quit()
