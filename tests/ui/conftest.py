import pytest
from selenium import webdriver

IMPLICIT_WAIT_TIMEOUT_S = 10
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_RESOLUTION = (WINDOW_WIDTH, WINDOW_HEIGHT)


@pytest.fixture(scope="session")
def browser():
    driver = webdriver.Chrome(keep_alive=True)
    driver.set_window_size(*WINDOW_RESOLUTION)
    driver.implicitly_wait(IMPLICIT_WAIT_TIMEOUT_S)

    yield driver

    driver.quit()
