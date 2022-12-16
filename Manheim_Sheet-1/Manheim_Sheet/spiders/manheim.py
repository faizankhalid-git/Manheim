import csv
import datetime
import os
import time

import scrapy
from scrapy import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class ManheimSpider(scrapy.Spider):
    name = 'manheim'
    custom_settings = {'FEED_URI': r'Output/Manheim_Data.csv', 'FEED_FORMAT': 'csv', }
    start_urls = ['https://dealer.dragspecialties.com']
    download_flag = input("Do you Want to Download the Files (y/n) --> ")
    region_flag = input("Do you Want to Add Region (y/n) --> ")
    grade_flag = input("Do you Want to Add Grade (y/n) --> ")
    options = webdriver.ChromeOptions()
    options.add_argument('--user-data-dir=c:\\temp\\profile3')
    prefs = {"profile.default_content_settings.popups": 0,
             "download.default_directory": f"{os.getcwd()}\Downloded_Files",
             "directory_upgrade": True}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.maximize_window()
    driver.execute_script("document.body.style.zoom='70%'")
    url = "https://mmr.manheim.com/?WT.svl=m_uni_hdr_buy&country=US&popup=true&source=man"

    def parse(self, no_response, **kwargs):
        self.driver.get(self.url)
        time.sleep(5)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "#user_username").send_keys('Obe1')
            self.driver.find_element(By.CSS_SELECTOR, "#user_password").send_keys('Azlan2021!!!')
            self.driver.find_element(By.CSS_SELECTOR, '[data-test="bttnSignIn"]').click()
        except:
            pass

        for row in list(csv.DictReader(open('input2.csv'))):
            try:
                self.driver.find_element(By.CSS_SELECTOR, '#vinText').clear()
                self.driver.find_element(By.CSS_SELECTOR, '#vinText').send_keys(row['VIN'])
                self.driver.find_element(By.CSS_SELECTOR, '[data-reactid="52"]').click()
                time.sleep(2)
                try:
                    checker = self.driver.find_element(By.XPATH,
                                                       '//*[contains(@class,"styles__modalContainer")]//h3').text
                    if checker:
                        yield {
                            'VIN': row['VIN'],
                            'Mileage': row['Mileage'],
                            'Base MMR': '',
                            'Avg. Odo': '',
                            'Avg. Cond': '',
                            'Adjustment MMR': '',
                            'Transaction': '',
                            'Lower Range': '',
                            'Upper Range': '',
                            'Grade': row['Grade'],
                            'Region': row['Region'],
                            'Date': datetime.datetime.now()
                        }
                        self.driver.find_element(By.CSS_SELECTOR, '.icon-cross').click()
                        continue
                except:
                    pass

                try:
                    odo_meter = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, 'input#Odometer')))
                    odo_meter.send_keys(row['Mileage'])
                except:
                    pass

                if self.region_flag.lower().strip() == 'y':
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[contains(@data-reactid,"226")]'))).click()
                        region = self.driver.find_elements(By.CSS_SELECTOR, '[data-reactid="222"] button')
                        for options in region:
                            if row['Region'] in options.text:
                                options.click()
                        break
                    except:
                        pass

                if self.grade_flag.lower().strip() == 'y':
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, '//*[contains(@data-reactid,"248")]'))).click()
                        region = self.driver.find_elements(By.CSS_SELECTOR, '[data-reactid="245"] button')
                        for options in region:
                            if row['Grade'] in options.text:
                                options.click()
                        break
                    except:
                        pass
                time.sleep(1)

                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-reactid="271"]')))
                response = Selector(text=self.driver.page_source)
                avf_odo = response.css('[data-reactid="135"]::text').get('')
                avg_cond = response.css('[data-reactid="139"]::text').get('')
                base_mmr = response.css('[data-reactid="129"]::text').get('')
                adjust_mmr = ''.join(response.css('[data-reactid="165"] *::text').getall())
                transactions = ''.join(response.css('[data-reactid="293"] *::text').getall())
                try:
                    transaction_count = transactions.split(' ')[-1]
                except:
                    transaction_count = transactions
                typical_range = ''.join(response.css('[data-reactid="158"] *::text').getall())
                lower_range, upper_range = '', ''
                try:
                    lower_range = typical_range.split('-')[0]
                    upper_range = typical_range.split('-')[1]
                except:
                    pass

                yield {
                    'VIN': row['VIN'],
                    'Mileage': row['Mileage'],
                    'Base MMR': base_mmr,
                    'Avg. Odo': avf_odo,
                    'Avg. Cond': avg_cond,
                    'Adjustment MMR': adjust_mmr,
                    'Transaction': transaction_count,
                    'Lower Range': lower_range,
                    'Upper Range': upper_range,
                    'Grade': row['Grade'],
                    'Region': row['Region'],
                    'Date': datetime.datetime.now()
                }
                if self.download_flag.lower().strip() == 'y':
                    self.driver.find_element(By.XPATH, '//a[contains(@class,"enabledExportLink")]').click()

            except:
                self.driver.get(self.url)
                time.sleep(5)
