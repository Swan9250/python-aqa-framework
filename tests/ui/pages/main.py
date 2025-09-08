import os
import yarl
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver


class MainPage:
    URL = yarl.URL(os.getenv("SITE_URL"))

    def __init__(self, browser: WebDriver) -> None:
        self.browser = browser
        self.header = (By.TAG_NAME, "header")
        self.logo = (By.CLASS_NAME, "top-level__logo")
        self.input_from = (By.CLASS_NAME, "cdek-input__input")
        self.label_where = (
            By.XPATH,
            '//div[@class="cdek-input__label" and contains(text(), "Куда")]',
        )
        self.work_area = (By.ID, "work-area")
        self.footer = (By.TAG_NAME, "footer")

    def get_header(self):
        return self.browser.find_element(*self.header)

    def get_logo(self):
        return self.browser.find_element(*self.logo).find_element(By.TAG_NAME, "img")

    def get_input_from(self):
        return self.browser.find_element(*self.input_from)

    def get_input_where(self):
        return self.browser.find_element(*self.label_where).find_element(
            By.XPATH, "following-sibling::input[1]"
        )

    def get_work_area(self):
        return self.browser.find_element(*self.work_area)

    def get_footer(self):
        return self.browser.find_element(*self.footer)
