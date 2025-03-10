from selenium import webdriver
import selenium.webdriver.chrome.service as ChromeService
import selenium.webdriver.chrome.options as ChromeOptions
import time

custom_browser_path = "C:/Program Files/Avast Software/Browser/Application/AvastBrowser.exe"
profile = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default"
extension_path = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/onochehmbbbmkaffnheflmfpfjgppblm/5.2.590_0"
extension_path2 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/dmfdacibleoapmpfdgonigdfinmekhgp/2.1.0.330_0"
extension_path3 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/beghmmhchncjignfbfnemngnlnjdmbcb/2.6.240_0"
extension_path4 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/gjcfnponmdkenfdibginkmlmediekpnm/1.32.1.1129_0"
extension_path5 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/hglfhehnlngcghjibkocbphocccdoipk/1.4.464_0"
extension_path6 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/lhnnoklckomcfdlknmjaenoodlpfdclc/1.4.0.104_0"
extension_path7 = "C:/Users/Noxx/AppData/Local/AVAST Software/Browser/User Data/Default/Extensions/mjcjbfohnabnpeahjjdeiimbinifjmad/0.0.136_0"

chrome_options = ChromeOptions.Options()

chrome_options.add_argument("--disable-features=ExtensionsToolbarMenu")  # Force extension visibility
chrome_options.add_argument("--enable-features=ExtensionsOnChromeUI")
chrome_options.add_argument("--disable-component-update")  # Prevent Avast from disabling its extension
chrome_options.add_argument("--force-fieldtrials=*Extensions/ForceEnabled/")  # Forces extensions to stay on
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)


chrome_options.add_argument(f"user-data-dir={profile}")  # Use the correct profile
chrome_options.add_argument(f"--load-extension={extension_path}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path2}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path3}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path4}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path5}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path6}")  # Manually load extension
chrome_options.add_argument(f"--load-extension={extension_path7}")  # Manually load extension
# use custom binary
chrome_options.binary_location = custom_browser_path


chromedriver_path = "./chromedriver_132.exe"
service = ChromeService.Service(chromedriver_path)

driver = webdriver.Chrome(service=service, options=chrome_options)

driver.get("http://dbctv.cz")

time.sleep(100)

driver.quit()