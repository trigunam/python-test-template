
import logging
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options

from suite.util import setup_logger

logger = logging.getLogger('chrome_driver')


class Driver:
    def __init__(self, path, page_load_timeout, result_folder, log_level):
        """
        Default Constructor
        """
        self.result_folder = result_folder
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--log-level={}'.format(log_level))

        setup_logger(logger, log_level)

        self.web_driver = None
        self.path = path
        self.chrome_options = chrome_options
        self.page_load_timeout = page_load_timeout

        self.init_driver()

    def init_driver(self):
        self.web_driver = webdriver.Chrome(self.path, options=self.chrome_options)
        self.web_driver.maximize_window()
        self.web_driver.implicitly_wait(30)
        self.web_driver.set_page_load_timeout(self.page_load_timeout)

    def get(self, url, retry):
        while True:
            try:
                retry -= 1
                self.web_driver.get(url)
                break
            except TimeoutException as terr:
                print('Timeout error while getting the driver.. {}'.format(terr))
                print('Retry with new driver....#{}'.format(retry))
                self.init_driver()
                if retry <= 0:
                    break
                continue
        return retry

    def title(self):
        return self.web_driver.title

    def quit(self):
        self.web_driver.quit()

    def find_element_by_id(self, id):
        return self.web_driver.find_element_by_id(id)

    def find_element_by_link_text(self, text):
        return self.web_driver.find_element_by_link_text(text)

    def find_element_by_xpath(self, xpath):
        return self.web_driver.find_element_by_xpath(xpath)

    def send_keys(self, key, value):
        """
        Send keys to the input text box.
        :param key: Find by xpath of this key
        :param value: Input this value to the xpath
        :return:
        """
        self.find_element_by_xpath(key).send_keys(value)

    def find_element_by_class_name(self, name):
        return self.web_driver.find_element_by_class_name(name)

    def save_screenshot(self, filename):
        self.web_driver.save_screenshot(''.join([self.result_folder, '/', filename, '.png']))
