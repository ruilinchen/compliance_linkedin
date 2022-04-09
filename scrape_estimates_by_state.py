"""
get estimated listings by state from linkedin: within 24 hours
"""
import pandas as pd
import time, random, string
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import keyring

username_key = keyring.get_password('linkedin', 'username') #need to set_password first
password_key = keyring.get_password('linkedin', 'password')

TODAY = str(int(datetime.today().strftime("%m%d%Y")))
OUTPUT_FILENAME = 'estimates_by_state.csv'

def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except NoSuchElementException:
        return False

def write_to_file(estimate_text, state):
    elements = [TODAY, state, estimate_text]
    with open(OUTPUT_FILENAME, 'a+') as f:
        f.write(','.join(elements))
        f.write('\n')

def get_scraped_states():
    df = pd.read_csv(OUTPUT_FILENAME, names=['date', 'state_abbr', 'estimated_jobs'])
    return set(df['state_abbr'][df['date'] == int(TODAY)])

scraped_states = get_scraped_states()
driver = webdriver.Firefox()
driver.get('https://linkedin.com/')
time.sleep(1)

### login first
username = driver.find_element_by_xpath('//*[@id="session_key"]')
password = driver.find_element_by_xpath('//*[@id="session_password"]')
username.send_keys(username_key)
password.send_keys(password_key)
# click the login button
login_btn = driver.find_element_by_xpath\
            ("//button[@class='sign-in-form__submit-button']")
time.sleep(1)
login_btn.click()

### iterate over all states
cities = pd.read_csv('custom_data/uscities.csv')
state2abbr = dict(zip(cities['state_name'], cities['state_id']))
for state_full, state_abbr in state2abbr.items():
    if state_abbr not in scraped_states:
        time.sleep(random.random()*3)
        #within the past week: f_TPR=r604800; with 24 hours: f_TPR=r86400; on_site: f_WT=1
        locator_url = f'https://www.linkedin.com/jobs/search/?f_TPR=r86400&f_WT=1&keywords=compliance&location={state_full}%2C%20United%20States&sortBy=R'
        driver.get(locator_url)
        # get the estimated result element
        survey_xpath = "//small"
        check_exists_by_xpath(driver, survey_xpath)
        estimate_element = driver.find_element_by_xpath(survey_xpath)
        estimate_text = estimate_element.text # this is the text. Example format: 2,333 results
        estimate_text = estimate_text.translate(str.maketrans('', '', string.punctuation)) # remove punctuations from the text

        write_to_file(estimate_text, state_abbr)

driver.close()
