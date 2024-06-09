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


class ShadowPaySkinScraper:
    def __init__(self, url):
        self.url = url
        self.driver = None
        self.setup_driver(url=url)

    def setup_driver(self, url):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.driver.set_window_size(1920, 1080)
        self.driver.get(url)
        self.wait = WebDriverWait(self.driver, 30)
        time.sleep(2)

    def close_modal_if_present(self):
        try:
            modal_close_button = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'div.base-modal.base-modal_state_fixed img[alt="close"]',
                    )
                )
            )
            if modal_close_button:
                modal_close_button.click()
                logger.info("Closed modal window.")
                self.wait.until_not(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.base-modal.base-modal_state_fixed")
                    )
                )
        except Exception as e:
            logger.info("No modal window found or failed to close modal window: {e}")

    def get_skins(self):
        skins = []

        try:
            try:
                self.close_modal_if_present()
                logger.info("Waiting for marketplace inventory to load...")
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.marketplace-items-list")
                    )
                )
            except:
                logger.error("Marketplace inventory did not load")
                return skins

            items = self.driver.find_elements(By.CSS_SELECTOR, "div.item-buy-card")
            logger.info(f"Found {len(items)} items.")

            for index in range(min(30, len(items))):

                items = self.driver.find_elements(By.CSS_SELECTOR, "div.item-buy-card")
                item = items[index]

                time.sleep(0.5)

                skin_name = item.find_element(
                    By.CSS_SELECTOR, "div.parse-color-item__name"
                ).text

                price = (
                    item.find_element(By.CSS_SELECTOR, "div.item-buy-card__sell-price")
                    .text.split("\n")[0]
                    .strip()
                )

                gun_type = item.find_element(
                    By.CSS_SELECTOR, "div.parseColorItemTransfer"
                ).text

                name = f"{skin_name} ({gun_type})"

                self.driver.execute_script("arguments[0].scrollIntoView();", item)

                click_attempts = 0
                clicked = False
                while click_attempts < 3 and not clicked:
                    try:
                        item.click()
                        clicked = True
                    except Exception as e:
                        logger.error(f"Click attempt {click_attempts + 1} failed: {e}")
                        time.sleep(1)
                        click_attempts += 1

                if not clicked:
                    logger.error("Failed to click item after 3 attempts")
                    continue

                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.marketplace-content")
                    )
                )

                share_link_element = self.driver.find_element(
                    By.CSS_SELECTOR, "input[data-v-0f0dccbb]"
                )
                share_link = share_link_element.get_attribute("value")

                try:
                    game_link_element = self.driver.find_element(
                        By.XPATH, '//a[contains(@href, "steam://rungame")]'
                    )
                    game_link = game_link_element.get_attribute("href")
                except:
                    game_link = None

                skin = Skin(name, price, share_link, game_link)
                skins.append(skin)

                self.driver.back()
                self.wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.marketplace-items-list")
                    )
                )
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error fetching skins: {e}")
            self.driver.save_screenshot("error_fetching_skins.png")

        return skins

    def close(self):
        self.driver.quit()
