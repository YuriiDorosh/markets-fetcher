from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def get_csgo_skins(url):
    options = Options()
    # options.headless = True  # Run Chrome in headless mode
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    

    # Setup Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.set_window_size(1920, 1080)
    
    try:
        driver.get(url)
        time.sleep(5)  # Wait for the page to fully load

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        items = []

        # Verify the content of the page
        print(soup.prettify()[:1000])  # Print the first 1000 characters of the parsed HTML for inspection

        # Find the section that contains the skins
        skin_section = soup.find('div', class_='c-assets__container')
        if not skin_section:
            print("Could not find the skin section.")
            return []

        print("Skin section found")

        # Find all the skins in the section
        skins = skin_section.find_all('asset-card')

        for skin in skins:
            name_tag = skin.find('img', class_='c-asset__img')
            price_tag = skin.find('span', class_='c-asset__priceNumber')
            image_tag = skin.find('img', class_='c-asset__img')

            name = name_tag['alt'] if name_tag else "N/A"
            price = price_tag.text.strip() if price_tag else "N/A"
            image_url = image_tag['src'] if image_tag else "N/A"

            items.append({
                'name': name,
                'price': price,
                'image_url': image_url
            })

        return items

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    finally:
        driver.quit()

if __name__ == "__main__":
    print("Script started")
    print(5)
    url = "https://dmarket.com/ingame-items/item-list/csgo-skins"
    skins = get_csgo_skins(url)
    if skins:
        for skin in skins:
            print(f"Name: {skin['name']}, Price: {skin['price']}, Image URL: {skin['image_url']}")
    else:
        print("No skins found")
