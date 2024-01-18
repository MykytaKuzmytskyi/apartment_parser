import re
import time
from datetime import datetime

import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class HousesSpider(scrapy.Spider):
    name = "houses"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent"]
    urls = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--enable-javascript")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
        self.driver = webdriver.Chrome(options=chrome_options)
        self.start_time = datetime.now()

    def parse(self, response: Response, **kwargs):
        final_urls = set()
        self.driver.get(response.url)
        time.sleep(1)

        while True:
            urls = self.driver.find_elements(By.CLASS_NAME, "a-more-detail")
            final_urls.update(url.get_attribute("href") for url in urls)

            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'next'))
            )

            if 'inactive' in next_button.get_attribute('class'):
                break
            next_button.click()
            time.sleep(1)

        for url in final_urls:
            yield scrapy.Request(url, callback=self.parse_detail)

    def parse_detail(self, response):
        self.driver.get(response.url)

        next_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.summary-photos a[role='button']"))
        )

        self.driver.execute_script("arguments[0].click();", next_button)
        time.sleep(1)

        but = self.driver.find_element(By.CSS_SELECTOR, "div.wrap")
        urls = []

        for image_num in range(1, len(self.driver.find_elements(By.CSS_SELECTOR, "div.carousel > ul > li > img"))):
            urls.append(but.find_element(By.TAG_NAME, "img").get_attribute("src"))
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(but)
            )
            next_button.click()

        title: str = response.css('span[data-id="PageTitle"]::text').get()

        address_region = response.css('h2[itemprop="address"]::text').get().strip().split(",")
        region: str = ''.join(address_region[1:]).strip()
        address: str = ''.join(address_region[:1])

        description: str = ''.join(response.css('div[itemprop="description"]::text').getall())
        price: int = int(response.css("span.text-nowrap::text").get().replace("$", "").replace(",", ""))
        num_text = ''.join(response.css("div.row.teaser div::text").getall())
        number: int = sum([int(num) for num in re.findall(r'\d+', num_text)])

        area = response.css("div.carac-value > span::text").get().strip().split()[0].replace(",", "")

        yield {
            "link": response.url,
            "title": title,
            "region": region,
            "address": address,
            "description": description.strip() if description else None,
            "photo_urls": urls,
            "price": price,
            "number_of_rooms": number,
            "area": int(area) if area.isnumeric() else None
        }

    def closed(self, reason):
        end_time = datetime.now()
        elapsed_time = end_time - self.start_time
        print(f"Script execution time: {elapsed_time}")

        self.driver.quit()