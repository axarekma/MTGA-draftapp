from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


def wait_and_click(browser, buttonstr, wait_for_element=10):
    time.sleep(1)
    element = WebDriverWait(browser, wait_for_element).until(
        EC.element_to_be_clickable((By.XPATH, buttonstr))
    )
    element.click()

# https://www.17lands.com/card_data?expansion=MKM&format=PremierDraft
def getdata(expansion, format="PremierDraft", deck_color=None):
    url = f"https://www.17lands.com/card_data?{expansion}=MKM&format={format}"
    if deck_color:
        url+=f"&deck_color={deck_color}"

    options = webdriver.ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.add_argument("headless")
    browser = webdriver.Chrome(options=options)

    browser.get(url)

    # wait_and_click(browser, f"//select[@name='expansion']/option[@value='{expansion}']")
    # wait_and_click(browser, f"//select[@name='format']/option[@value='{format}']")
    # if deck_color:
    #     wait_and_click(
    #         browser, f"//select[@name='deck_color']/option[@value='{deck_color}']"
    #     )

    WebDriverWait(browser, 5).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@class='list_card_name']"))
    )

    time.sleep(2)

    soup = BeautifulSoup(browser.page_source, "html.parser")

    browser.quit()

    table = soup.findAll("table", {"class": "table"})
    with open("__table__.html", "w") as file:
        file.write(str(table))

    df = pd.read_html("__table__.html")[0]
    return df
