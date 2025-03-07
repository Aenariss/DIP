from selenium import webdriver
import selenium.webdriver.chrome.service as ChromeService
import time
import selenium.webdriver.chrome.options as ChromeOptions

custom_browser_path = "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"

chrome_options = ChromeOptions.Options()
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--enable-javascript")

# use custom binary
chrome_options.binary_location = custom_browser_path

# Important to check chromedriver version compatibility with specified browser (manually)
chromedriver_path = "./chromedriver.exe"


# Go through all specified extensions and add them
# Will not be used in the thesis, but allows more potential flexibility
#try:
#    for extension in options.get(TESTED_ADDONS):
#        chrome_options.add_extension(CHROME_ADDONS_FOLDER + extension)
#except Exception:
#    print(f"Error loading extension {extension}. Is it present in {CHROME_ADDONS_FOLDER}?")
#    exit(GENERAL_ERROR)

service = ChromeService.Service(chromedriver_path)

driver = webdriver.Chrome(service=service, options=chrome_options)

print("OK")

# Problem - BRAVE stahuje adblock listy dynamiocky, ale kdyz ja udelam vlastni DNS a blokuju firewall, tak toho moc nestahne - jak vyresit?
driver.get("http://dbctv.cz")
time.sleep(50)