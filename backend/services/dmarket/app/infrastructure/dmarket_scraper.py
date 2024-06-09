import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from app.domain.skin import Skin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DMartSkinScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.driver.set_window_size(1920, 1080)

    def search_skins(self, search_term, price_from=None, price_to=None):
        self.driver.get(self.url)
        time.sleep(1)

        search_input = self.driver.find_element(
            By.CSS_SELECTOR, "input.o-filter__searchInput"
        )
        search_input.send_keys(search_term)

        if price_from is not None:
            price_from_input = self.driver.find_element(
                By.CSS_SELECTOR, 'input[formcontrolname="priceFrom"]'
            )
            price_from_input.clear()
            price_from_input.send_keys(str(price_from))

        if price_to is not None:
            price_to_input = self.driver.find_element(
                By.CSS_SELECTOR, 'input[formcontrolname="priceTo"]'
            )
            price_to_input.clear()
            price_to_input.send_keys(str(price_to))

        search_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[aria-label="Search"]'
        )
        self.driver.execute_script("arguments[0].click();", search_button)

        time.sleep(1)

    def get_skin_details(self, skin_index):
        # Refetch the skin elements
        skins = self.driver.find_elements(By.CSS_SELECTOR, "asset-card")
        if skin_index >= len(skins):
            return None
        skin = skins[skin_index]

        try:
            name_tag = skin.find_element(By.CSS_SELECTOR, "img.c-asset__img")
            price_tag = skin.find_element(By.CSS_SELECTOR, "span.c-asset__priceNumber")
            name = name_tag.get_attribute("alt") if name_tag else "N/A"
            price = price_tag.text.strip() if price_tag else "N/A"
        except Exception as e:
            logger.error(
                f"Error retrieving name or price for skin {skin_index + 1}: {e}"
            )
            return None

        try:
            info_icon = skin.find_element(By.CSS_SELECTOR, "i.c-asset__actionIcon")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", info_icon)
            self.driver.execute_script("arguments[0].click();", info_icon)
        except Exception as e:
            logger.error(f"Error clicking info icon for skin {skin_index + 1}: {e}")
            return None

        time.sleep(1)

        try:
            onboarding_close_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "mat-icon.c-exchangeTabOnboarding__close")
                )
            )
            onboarding_close_button.click()
            time.sleep(1)
        except Exception as e:
            logger.error("No onboarding popup detected")

        try:
            overlay = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.cdk-overlay-pane")
                )
            )
        except Exception as e:
            logger.error(f"Error loading overlay for skin {skin_index + 1}: {e}")
            return None

        try:
            copy_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        'button[data-test-id="shareLinkOpenPopUp_clickInfo"]',
                    )
                )
            )
            self.driver.execute_script("arguments[0].click();", copy_button)
            time.sleep(1)
        except Exception as e:
            logger.error(f"Error clicking copy button for skin {skin_index + 1}: {e}")
            return None

        try:
            share_link_input = self.driver.find_element(
                By.CSS_SELECTOR, "input.c-shareLink__input"
            )
            share_link = share_link_input.get_attribute("value")
        except Exception as e:
            logger.error(f"Error retrieving share link for skin {skin_index + 1}: {e}")
            return None

        try:
            game_link_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a.c-assetPreviewButtons__button")
                )
            )
            game_link = game_link_element.get_attribute("href")
        except Exception as e:
            logger.error(f"Error retrieving game link for skin {skin_index + 1}: {e}")
            return None

        try:
            close_button = self.driver.find_element(
                By.CSS_SELECTOR, 'button[aria-label="Close"]'
            )
            self.driver.execute_script("arguments[0].click();", close_button)
            time.sleep(1)  # Wait to ensure popup is closed
        except Exception as e:
            logger.error(f"Error closing popup for skin {skin_index + 1}: {e}")
            return None

        return Skin(name, price, share_link, game_link)

    def get_skins(self, search_term, price_from=None, price_to=None):
        items = []
        self.search_skins(search_term, price_from, price_to)

        for index in range(15):
            details = self.get_skin_details(index)
            if details:
                items.append(details)
            else:
                break

            self.driver.get(self.url)
            self.search_skins(search_term, price_from, price_to)
            time.sleep(1)

        return items

    def close(self):
        self.driver.quit()
