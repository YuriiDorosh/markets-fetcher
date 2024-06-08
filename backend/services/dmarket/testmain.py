from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os

class DMartSkinScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.set_window_size(1920, 1080)

    def search_skins(self, search_term, price_from=None, price_to=None):
        self.driver.get(self.url)
        time.sleep(5)  # Wait for the page to fully load

        # Locate the search input box and enter the search term
        search_input = self.driver.find_element(By.CSS_SELECTOR, 'input.o-filter__searchInput')
        search_input.send_keys(search_term)
        
        # Set price filter if provided
        if price_from is not None:
            price_from_input = self.driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="priceFrom"]')
            price_from_input.clear()
            price_from_input.send_keys(str(price_from))
        
        if price_to is not None:
            price_to_input = self.driver.find_element(By.CSS_SELECTOR, 'input[formcontrolname="priceTo"]')
            price_to_input.clear()
            price_to_input.send_keys(str(price_to))
        
        # Submit the search using JavaScript click to avoid intercept issues
        search_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Search"]')
        self.driver.execute_script("arguments[0].click();", search_button)
        
        time.sleep(5)  # Wait for the search results to load

    def get_skins(self):
        page_source = self.driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        items = []

        # Find the section that contains the skins
        skin_section = soup.find('div', class_='c-assets__container')
        if not skin_section:
            print("Could not find the skin section.")
            return []

        # Find all the skins in the section
        skins = skin_section.find_all('asset-card')

        for index, skin in enumerate(skins):
            name_tag = skin.find('img', class_='c-asset__img')
            price_tag = skin.find('span', class_='c-asset__priceNumber')
            image_tag = skin.find('img', class_='c-asset__img')

            name = name_tag['alt'] if name_tag else "N/A"
            price = price_tag.text.strip() if price_tag else "N/A"
            image_url = image_tag['src'] if image_tag else "N/A"

            # Click on the info icon to get the details
            try:
                info_icon = self.driver.find_elements(By.CSS_SELECTOR, 'i.c-asset__actionIcon')[index]
                self.driver.execute_script("arguments[0].click();", info_icon)
                print(f"Clicked info icon for skin {index + 1}")
            except Exception as e:
                print(f"Error clicking info icon for skin {index + 1}: {e}")
                continue
            
            time.sleep(2)  # Wait for the popup to load

            # Check if the popup is loaded
            try:
                overlay = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cdk-global-overlay-wrapper'))
                )
                print("Overlay loaded successfully")
            except Exception as e:
                print(f"Error loading overlay for skin {index + 1}: {e}")
                continue

            # Get the share link from the input field in the dialog
            try:
                share_link_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.c-shareLink__dialog input[readonly="true"]'))
                )
                share_link = share_link_input.get_attribute('value') if share_link_input else "N/A"
                print(f"Found share link: {share_link}")
            except Exception as e:
                print(f"Error finding share link input for skin {index + 1}: {e}")
                # Take a screenshot for debugging
                screenshot_path = os.path.join(os.getcwd(), f"error_skin_{index + 1}.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
                share_link = "N/A"

            # Close the popup
            try:
                close_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.mat-dialog-close'))
                )
                close_button.click()
                time.sleep(1)  # Wait for the popup to close
                print("Popup closed successfully")
            except Exception as e:
                print(f"Error closing popup for skin {index + 1}: {e}")

            items.append({
                'name': name,
                'price': price,
                'image_url': image_url,
                'share_link': share_link
            })

        return items

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    print("Script started")
    print(5)
    url = "https://dmarket.com/ingame-items/item-list/csgo-skins"
    search_term = "knife"  # You can change this to any search term you want
    price_from = 100
    price_to = 1000
    
    scraper = DMartSkinScraper(url)
    scraper.search_skins(search_term, price_from, price_to)
    skins = scraper.get_skins()
    scraper.close()

    if skins:
        for skin in skins:
            print(f"Name: {skin['name']}, Price: {skin['price']}, Image URL: {skin['image_url']}, Share Link: {skin['share_link']}")
    else:
        print("No skins found")
