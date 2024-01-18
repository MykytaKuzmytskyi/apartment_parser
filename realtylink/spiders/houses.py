import re
import time

import scrapy
from scrapy.http import Response
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class HousesSpider(scrapy.Spider):
    name = "houses"
    allowed_domains = ["realtylink.org"]
    start_urls = ["https://realtylink.org/en/properties~for-rent"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response: Response, **kwargs):
        final_urls = set()
        self.driver.get(response.url)

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

    def closed(self, reason):
        self.driver.quit()
