from pages.main import MainPage


def test_open_main_page(browser):
    main_page = MainPage(browser)
    browser.get(main_page.URL.human_repr())
    assert main_page.get_header().is_displayed(), "Header is not displayed"
    assert main_page.get_work_area().is_displayed(), "Work area is not displayed"
    assert main_page.get_footer().is_displayed(), "Footer is not displayed"
    assert main_page.get_logo().is_displayed(), "Logo is not displayed"
