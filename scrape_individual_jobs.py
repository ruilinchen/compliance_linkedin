"""
get individual jobs from linkedin
"""
import pandas as pd
import time, random, string
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import keyring
from selenium.webdriver.common.by import By

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

### iterate over the list of urls
job_df = pd.read_csv('job_url_data/job_title_URLs.csv')
job_df['job_id'] = job_df['url'].str.split('/').str[5] # extract job_id from url
job2url = dict(zip(job_df['job_id'], job_df['url']))
for job_id, job_url in job2url.items():
    time.sleep(random.random()*3)
    driver.get(job_url)
    see_more_xpath = "//button[@aria-label='Click to see more description']"
    see_more_btn = driver.find_element_by_xpath(see_more_xpath)
    see_more_btn.click()
    page_source = driver.page_source
    with open(f"webpage_data/{job_id}.html", "w") as f:
        f.write(page_source)
driver.close()