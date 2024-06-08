from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

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
        time.sleep(2)  # Wait for the page to fully load

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
        
        time.sleep(2)  # Wait for the search results to load

    def get_skins(self):
        items = []

        # Find all the skins in the section
        skins = self.driver.find_elements(By.CSS_SELECTOR, 'asset-card')

        if not skins:
            print("Could not find any skins.")
            return []

        for index, skin in enumerate(skins):
            # Get name and price for the skin
            try:
                name_tag = skin.find_element(By.CSS_SELECTOR, 'img.c-asset__img')
                price_tag = skin.find_element(By.CSS_SELECTOR, 'span.c-asset__priceNumber')
                name = name_tag.get_attribute('alt') if name_tag else "N/A"
                price = price_tag.text.strip() if price_tag else "N/A"
            except Exception as e:
                print(f"Error retrieving name or price for skin {index + 1}: {e}")
                continue

            # Click on the info icon to get the details
            try:
                # info_icon = skin.find_element(By.CSS_SELECTOR, 'i.c-asset__actionIcon')
                # self.driver.execute_script("arguments[0].click();", info_icon)
                # print(f"Clicked info icon for skin {index + 1}")
                info_icon = skin.find_element(By.CSS_SELECTOR, 'i.c-asset__actionIcon')
                self.driver.execute_script("arguments[0].scrollIntoView(true);", info_icon)
                self.driver.save_screenshot(f'info_icon_skin_{index + 1}.png')
                self.driver.execute_script("arguments[0].click();", info_icon)
                print(f"Clicked info icon for skin {index + 1}")
            except Exception as e:
                print(f"Error clicking info icon for skin {index + 1}: {e}")
                continue
                
            time.sleep(2)  # Wait for the popup to load

            # Check for the onboarding popup and close it if present
            try:
                onboarding_close_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'mat-icon.c-exchangeTabOnboarding__close'))
                )
                onboarding_close_button.click()
                time.sleep(1)  # Wait for the onboarding popup to close
            except Exception as e:
                print("No onboarding popup detected")

            # Check if the detail info popup is loaded
            try:
                overlay = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.cdk-overlay-pane'))
                )
            except Exception as e:
                print(f"Error loading overlay for skin {index + 1}: {e}")
                continue

            # Click the copy button to copy the share link to the clipboard
            try:
                copy_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-test-id="shareLinkOpenPopUp_clickInfo"]'))
                )
                self.driver.execute_script("arguments[0].click();", copy_button)
            except Exception as e:
                print(f"Error clicking copy button for skin {index + 1}: {e}")
                continue

            # Get the copied link from the input field
            try:
                share_link_input = self.driver.find_element(By.CSS_SELECTOR, 'input.c-shareLink__input')
                share_link = share_link_input.get_attribute('value')
            except Exception as e:
                print(f"Error finding share link input for skin {index + 1}: {e}")
                continue
            
            # Get the game link URL
            try:
                game_link_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'a.c-assetPreviewButtons__button'))
                )
                game_link = game_link_element.get_attribute('href')
                print(f"Game link for skin {index + 1}: {game_link}")  # Debugging line
            except Exception as e:
                print(f"Error retrieving game link for skin {index + 1}: {e}")
                continue

            items.append({
                'name': name,
                'price': price,
                'share_link': share_link,
                'game_link': game_link
            })

            # Close the detail info popup
            try:
                close_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Close"]')
                self.driver.execute_script("arguments[0].click();", close_button)
            except Exception as e:
                print(f"Error closing popup for skin {index + 1}: {e}")

            # Break the loop if we have collected 50 skins
            # if len(items) >= 50:
            if len(items) >= 5:
                break

        return items

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    print("Script started")
    url = "https://dmarket.com/ingame-items/item-list/csgo-skins"
    scraper = DMartSkinScraper(url)
    # scraper.search_skins("Butterfly Knife")
    scraper.search_skins("Sport Gloves")
    skins = scraper.get_skins()
    if skins:
        for skin in skins:
            print(f"Name: {skin['name']}, Price: {skin['price']}, Share Link: {skin['share_link']}, Game Link: {skin['game_link']}")
    else:
        print("No skins found")
    scraper.close()
