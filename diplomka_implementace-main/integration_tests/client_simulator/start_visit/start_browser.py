#
#  Copyright (C) 2019  Amit Datta
#  Copyright (C) 2024  Jana Petranova
#
# SPDX-License-Identifier: GPL-3.0-or-later
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import time                                 
import sys                                 
import os                                   
from selenium import webdriver             

from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .client_side_tests.domain_level_settings_test import *
from .client_side_tests.NBS_settings_test import *

browser_versions = ["stable", "dev", "beta", "canary", "esr", "nightly"]

"""
In case Selenium Manager times out, try to downlaod the browser driver again.

    firefox_options : options from the Webdriver library

    ------------------------------------------------------

    driver : Webdriver object
"""
def create_webdriver(firefox_options):
    try:
        driver = webdriver.Firefox(options=firefox_options)
        return driver
    except WebDriverException as e:
        print("Failed to fetch driver:", e.msg)
        print("Retrying in 5 seconds...")
        time.sleep(5) 
        return create_webdriver(firefox_options)


"""
Find JShelter Options Page. Must be done seperately for both Firefox and Chrome.
    browser : str
        Browser type.
    driver : Webdriver object

    ------------------------------------------------------

    options_page : str
        JShelter options page.
"""
def find_jshelter_options_page(browser, version, driver):
    options_page = None
    if "firefox" in browser:
        #Change the JShelter level in Firefox.       
        driver.get("about:debugging#/runtime/this-firefox")
        time.sleep(0.5)
        element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(("xpath", "//span[@title='JShelter']"))
        )
        parent_li = element.find_element("xpath", "./..")
        uuid_element = parent_li.find_element("xpath","./section/dl/div[@class='fieldpair'][2]/dd")
        uuid = uuid_element.text
        options_page = f"moz-extension://{uuid}/options.html"

    if "chrome" in browser:
        #Change the JShelter level in Chrome.  
        if int(version.split('.')[0]) >= 126:
            driver.get("chrome://extensions/")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(("xpath", "/html/body/extensions-manager")))
            manager_shadow_root = driver.execute_script('return document.querySelector("extensions-manager").shadowRoot')
            toolbar = manager_shadow_root.find_element("css selector", "#toolbar")
            dev_mode_toggle = driver.execute_script('return arguments[0].shadowRoot.querySelector("#devMode")', toolbar)
            dev_mode_toggle.click()
            time.sleep(1)
            container = manager_shadow_root.find_element("css selector", "#container #viewManager #items-list")
            items_container = driver.execute_script('return arguments[0].shadowRoot.querySelector("#extensions-section > div")', container)
            extensions_items = items_container.find_elements("tag name","extensions-item")
            for item in extensions_items:
                item_text_content = driver.execute_script('return arguments[0].shadowRoot.querySelector("#name").innerText', item)
                if item_text_content == "JShelter":
                    extension_id = item.get_attribute("id")
            options_page = f"chrome-extension://{extension_id}/options.html" 
            
        else:
            driver.get("chrome://extensions/")
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(("xpath", "/html/body/extensions-manager")))
            manager_shadow_root = driver.execute_script('return document.querySelector("extensions-manager").shadowRoot')
            toolbar = manager_shadow_root.find_element("css selector", "#toolbar")
            dev_mode_toggle = driver.execute_script('return arguments[0].shadowRoot.querySelector("#devMode")', toolbar)
            dev_mode_toggle.click()
            time.sleep(1)
            container = manager_shadow_root.find_element("css selector", "#container #viewManager #items-list")
            items_container = driver.execute_script('return arguments[0].shadowRoot.querySelector("#content-wrapper > div:nth-child(4)")', container)
            extensions_items = items_container.find_elements("tag name","extensions-item")
            for item in extensions_items:
                item_text_content = driver.execute_script('return arguments[0].shadowRoot.querySelector("#name").innerText', item)
                if item_text_content == "JShelter":
                    extension_id = item.get_attribute("id")
            options_page = f"chrome-extension://{extension_id}/options.html" 
    
    return options_page


"""
Names and locations of extensions are configured through this class. 
If you'd like to add another extension to the program, you have to add it to the dictionary here.

"""
class PetConfig:
    def __init__(self):
        #These two dictionaries represent key-value pairs of extension abbreviation-extension name. Each dictionary represents one possible browser to set up.
        #In order to add a new extension you must create a new key-value pair in both dictionaries. 
        #The key will be used to recognize the extension inside the client configuration file, the value represents the extension name.

        self.petfco={
                "UO": "uBlock_Origin_f",
                "PB": "Privacy_Badger_f",
                "NS": "NoScript_f",
                "DDGPE": "DuckDuckGoPE_f",
                "Gh": "Ghostery_f",
                "NC": "NetCraft_f",
                "DE": "Decentraleyes_f",
                "JS": "JShelter_f",
                "CB": "CanvasBlocker_f"
                }

        self.petcco={
                "UO": "uBlock_Origin_c",
                "PB": "Privacy_Badger_c",
                "NS": "NoScript_c",
                "DDGPE": "DuckDuckGoPE_c",
                "Gh": "Ghostery_c",
                "NC": "NetCraft_c",
                "DE": "Decentraleyes_c",
                "JS": "JShelter_c",
                "CB": "CanvasBlocker_c"}

        #These two dictionaries represent key-value pairs of extension name-extension file. Each dictionary represents one possible browser to set up.
        ##In order to add a new extension you must create a new key-value pair in both dictionaries. 
        #The key will be used to recognize the extension name from the previous dictionaries, the value will represent the extension file.

        self.petf = {"None":"", 
                "uBlock_Origin_f": "uBlock0@raymondhill.net.xpi",
                "Privacy_Badger_f": "PrivacyBadger@jetpack.xpi",
                "NoScript_f": "NoScript.xpi",
                "DuckDuckGoPE_f": "DuckDuckGoPE.xpi",
                "Ghostery_f": "firefox@ghostery.com.xpi", 
                "NetCraft_f": "Net_Craft.xpi",
                "Decentraleyes_f": "Decentraleyes.xpi",
                "JShelter_f": "jsr@javascriptrestrictor.xpi",
                "CanvasBlocker_f" : "CanvasBlocker@kkapsner.de.xpi"}

        self.petc = {"None":"",  
                "uBlock_Origin_c": "uBlockOrigin.crx",
                "Privacy_Badger_c": "PrivacyBadger.crx",
                "NoScript_c": "NoScript.crx",
                "DuckDuckGoPE_c": "DuckDuckGoPE.crx",
                "Ghostery_c": "Ghostery.crx", 
                "NetCraft_c": "Netcraft.crx",
                "Decentraleyes_c": "Decentraleyes.crx",
                "JShelter_c": "JShelter.crx",
                "CanvasBlocker_c": "CanvasBlocker.crx"}

        self.pet = {"firefox":self.petf,"chrome":self.petc}
        self.petco = {"firefox":self.petfco,"chrome":self.petcco}

        self.addons_path = {"firefox" : os.path.join("addons","firefox"),
                            "chrome" : os.path.join("addons","chrome") }
                         

    """
    Retrieve the extension files so they could be installed. Also check if JShelter is being tested, so it could be set up later. This could be configured
    by developers to activate their own extension settings.

        my_pets : [str]
            List of extensions to test.
        my_browser : str
            Name and version of the browser.
        
        ------------------------------------------------------

        totalPaths : [str]
            List of extension files locations.
        JSlevel : str
            The level of JShelter to be tested.
    """
    def getExtensionsPath(self,my_pets,my_browser):

        cwd = os.path.dirname(os.path.abspath(__file__))

        pets_to_test = []   
        my_browser, *version = my_browser.split('=')

        JSlevel = None

        for oneAddon in my_pets:
            oneAddon, *testing_level = oneAddon.split('_')
            #If you'd like to configure you extension, you can save the settings variable here. The variable will be saved as anything after _.
            #For example in case of JShelter - either JS_0, JS_1, JS_2, JS_3, JS_NBS or JS_DLS can be tested.
            if testing_level: JSlevel = testing_level[0]
            if oneAddon in self.petco[my_browser].keys(): 
                pets_to_test.append(self.petco[my_browser][oneAddon])
        
        pathList = []
 
        for oneAddon in pets_to_test:
            pathList.append(self.pet[my_browser][oneAddon])

        totalPaths = []

        for oA in pathList:      
                if oA != "":  totalPaths.append(os.path.join(cwd, self.addons_path[my_browser], oA))
        
        if JSlevel:
            return totalPaths, None, JSlevel
        else:
            return totalPaths, None 

'''
Class representing a browser instance.

    browser : str
        Name and version of the browser.
    pets : [str]
        List of extensions to test.
    proxy_settings : dict
        Proxy settings for the browser.
    
'''
class Browser:
    
    def __init__(self, browser, pet, proxy_setting):

        """
        If given valid proxy settings, this function will configure socks5 proxy properly on chrome and firefox.
        """
        def setup_socks5_proxy(browser, profile, proxy_setting):
            if proxy_setting is not None:
                address = proxy_setting["address"]
                port = proxy_setting["port"]
                bypass_list = proxy_setting["bypass-list"]

                if "chrome" in browser.lower():
                    # https://sordidfellow.wordpress.com/2015/05/21/ssh-tunnel-for-chrome/
                    profile.add_argument("--proxy-server=socks5://%s:%s" % (address, port))
                    profile.add_argument("--proxy-bypass-list=%s" % bypass_list)
                    print("socks5 proxy configured on chrome")

                elif "firefox" in browser.lower():
                    # https://developer.mozilla.org/en-US/docs/Mozilla/Preferences/Mozilla_networking_preferences
                    profile.set_preference("network.proxy.type", 1)
                    profile.set_preference("network.proxy.socks", address)
                    profile.set_preference("network.proxy.socks_port", port)
                    profile.set_preference("network.proxy.socks_version", 5)
                    profile.set_preference("network.proxy.socks_remote_dns", "true")
                    profile.set_preference("network.proxy.no_proxies_on", bypass_list)
                    print("socks5 proxy configured on firefox")

        self.pet_names = pet
        pet_config = PetConfig()
        #The set up for individual extensions on individual browsers can vary immensely, it's not really possible to create a uniform function.
        #This is due to the set up being executed client-side, different set up pages can have different DOM model on different browsers. 
        #Also the way browsers name installed extensions is inconsistent. 
        #So it's up to the developer to do their own set up.

        totalPaths, config, *JSlevel = pet_config.getExtensionsPath(pet,browser)
        
        ghostery_tested = False
        browser_type, *version = browser.split('=')
        matched_type = next((bt for bt in browser_versions if bt in browser.lower()), None)

        if "firefox" in browser.lower():
            
            fp = webdriver.FirefoxProfile()
            firefox_options = webdriver.FirefoxOptions()
            setup_socks5_proxy("firefox", fp, proxy_setting)
            if version:
                firefox_options.browser_version=str(version[0])

            fp.set_preference("geo.enabled", True)
            fp.set_preference('geo.prompt.testing', True)
            fp.set_preference('geo.prompt.testing.allow', True)
            fp.set_preference("geo.provider.testing", True)
            fp.set_preference("geo.provider.network.url", "https://location.services.mozilla.com/v1/geolocate?key=test")
            fp.set_preference("accept_insecure_certs", True)
            fp.set_preference("media.navigator.enabled", True)
            fp.set_preference("media.navigator.permission.disabled", True)
            fp.set_preference("media.autoplay.ask-permission", False)
            fp.set_preference("media.autoplay.blocking_policy", 2)
            fp.set_preference("media.navigator.streams.fake", True)
            fp.set_preference("services.sync.prefs.sync.media.autoplay.default", True)
            fp.set_preference("media.autoplay.default", 0)
            firefox_options.profile = fp
            firefox_options.add_argument("--no-sandbox")
            firefox_options.add_argument("--use-fake-ui-for-media-stream")


            self.driver = create_webdriver(firefox_options)

            session_details = self.driver.capabilities
            browser_version = session_details['browserVersion']

            if matched_type:
                self.browser_and_version = f"firefox={browser_version}{matched_type}"
            else:
                self.browser_and_version = f"firefox={browser_version}"
            
            #Install extensions.
            if (totalPaths != "No addons to install"):
                for addon in totalPaths:     
                    if "ghostery" in addon.lower():      
                        ghostery_tested = True    
                    self.driver.install_addon(addon)   

            #At this point all listed extensions are installed. If you wish to configure them you can do so from this point on till the end of the 
            #object class.

            if ghostery_tested:
                time.sleep(0.5)
                for window_handle in self.driver.window_handles:
                    self.driver.switch_to.window(window_handle)
                    if self.driver.title == "Welcome to Ghostery":
                        try:
                            element = WebDriverWait(self.driver, 30).until(
                                EC.presence_of_element_located(("xpath", "/html/body/ui-onboarding-short/ui-onboarding-layout/ui-onboarding-short-main-view/ui-onboarding-card/div[2]/div[2]/ui-button"))
                            )
                            element.click()
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            break
                        except Exception as e:
                            print("error ", e)

            if JSlevel:    
                #Change the JShelter level in Firefox.       
                options_page = find_jshelter_options_page(browser.lower(), browser_version, self.driver)

                if JSlevel[0] == "NBS":
                    test_switching_NBS(self.driver, options_page, browser_type)
                    return
                
                if JSlevel[0] == "DLS":
                    test_setting_domain_level(self.driver, options_page)
                    test_change_domain_level(self.driver, options_page)
                    return

                self.driver.get(options_page)
                select_level = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(("id", "level-" + str(JSlevel[0])))
                    )
                select_level.click()
                time.sleep(1)


        elif "chrome" in browser.lower():
            chrome_options = webdriver.ChromeOptions()
            setup_socks5_proxy("chrome", chrome_options, proxy_setting)

            #Install extensions.
            if (totalPaths):
                for addon in totalPaths:
                    if "ghostery" in addon.lower():      
                        ghostery_tested = True    
                    chrome_options.add_extension(addon)

            if version:
                chrome_options.browser_version=str(version[0])
            
            
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument('--disable-dev-shm-usage')   
            chrome_options.add_argument('--ignore-certificate-errors')   
            chrome_options.add_argument("--dns-prefetch-disable")
            chrome_options.add_argument("enable-automation")
            chrome_options.add_argument("--use-fake-ui-for-media-stream")
            self.driver = webdriver.Chrome(options=chrome_options)

            session_details = self.driver.capabilities
            browser_version = session_details['browserVersion']

            if matched_type:
                self.browser_and_version = f"chrome={browser_version}{matched_type}"
            else:
                self.browser_and_version = f"chrome={browser_version}"

            #At this point all listed extensions are installed. If you wish to configure them you can do so from this point on till the end of the 
            #object class.

            if ghostery_tested:
                time.sleep(0.5)
                for window_handle in self.driver.window_handles:
                    self.driver.switch_to.window(window_handle)
                    if self.driver.title == "Welcome to Ghostery":
                        try:
                            element = WebDriverWait(self.driver, 30).until(
                                EC.presence_of_element_located(("xpath", "/html/body/ui-onboarding/ui-onboarding-layout/ui-onboarding-main-view/ui-onboarding-card/div[2]/div[2]/ui-button[1]"))
                            )
                            element.click()
                            self.driver.close()
                            self.driver.switch_to.window(self.driver.window_handles[0])
                            break
                        except Exception as e:
                            print("error ", e)

            if JSlevel:
                # Change the JShelter level in Chrome.
                options_page = options_page = find_jshelter_options_page(browser.lower(), browser_version, self.driver)

                if JSlevel[0] == "DLS":
                    test_setting_domain_level(self.driver, options_page)
                    test_change_domain_level(self.driver, options_page)
                    return
                
                self.driver.get(options_page)
                time.sleep(1)
                select_level = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located(("id", "level-" + str(JSlevel[0])))
                    )
                select_level.click()
                time.sleep(1)

        else:
            print("Unsupported Browser")
            sys.exit(0)

    def get_version(self):
        return self.browser_and_version

    def quit(self):
        try:
            self.driver.quit()
        except:
            self.driver.close() 

    """
    Visits all pages in site_list with delay

        site_list : [str]
            List of sites to visit.
        delay : int
            Time spent on test page.
    """
    def visit_sites(self, site_list, delay): 
        print("Browser currently tested: " + self.get_version() + "\n" + "Extensions installed: " + ", ".join(self.pet_names))
        for site in site_list:         
            self.driver.set_page_load_timeout(delay + 60)
            sys.stdout.write(". \n")
            sys.stdout.flush()
            try:                          
                self.driver.get(site)
                self.driver.switch_to.window(self.driver.window_handles[0])  
                time.sleep(2)
                self.driver.find_element("id", "play").click()
                time.sleep(delay)
            except TimeoutException:
                 print("Page load timed out, retrying.")
                 self.driver.switch_to.new_window('window')
                 self.visit_sites((site_list[(site_list.index(site)):]), delay)

            except KeyboardInterrupt:
                print("Interrupted by keyboard, shutting down.")
                exit(0)
            except:
                print("Unexpected error:", sys.exc_info())
