from driver_setup import setup_driver

def test_driver():
    driver, wait = setup_driver()
    try:
        # Open a test website
        driver.get("https://www.google.com")
        print("Title of the page is:", driver.title)
    finally:
        driver.quit()

if __name__ == "__main__":
    test_driver()