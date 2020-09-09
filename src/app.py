from utils.browser import set_chrome_driver
from utils.tools import run_on_thread
from utils.logger import logger

import json
import time
from selenium.webdriver.common.by import By

SEARCH_URL = "https://app.tzuchi.com.tw/tchw/opdreg/DtQuery.aspx?Loc=TC"

#邱慧玲
#109/10/09

def execute_register(patient: dict) -> None:
    try:
        driver = set_chrome_driver()
        driver.get(SEARCH_URL)
        search_bar = driver.find_element(By.CSS_SELECTOR, 'input[name="ctl00$ContentPlaceHolder1$tbxDt"]')
        search_bar.send_keys(patient['doc_name'])
        search_button = driver.find_element(By.CSS_SELECTOR, 'input[name="ctl00$ContentPlaceHolder1$btnDtQuery"]')
        search_button.click()
        time.sleep(1)
        # get date table
        schedule = driver.find_elements(By.CSS_SELECTOR, 'table[id="ctl00_ContentPlaceHolder1_gvDtQuery"] > tbody > tr')

        # get page list --> start at last page
        found_date = False
        page_list = schedule[-1].find_elements(By.CSS_SELECTOR, 'a')

        page_list[-1].click()
        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, 'table[id="ctl00_ContentPlaceHolder1_gvDtQuery"] > tbody > tr')
        for j in range(2, len(rows)-1):
            values = rows[j].find_elements(By.CSS_SELECTOR, 'td')
            date = values[1].text
            if date == patient['target_date']:
                found_date = True
                values[0].click()
                break
        
        if not found_date:
            logger.error('unable to find the target date, 指定日期不存在')
        
        id_bar = driver.find_element(By.CSS_SELECTOR, 'input[name="txtMRNo"]')
        id_bar.send_keys(patient['id'])
        time.sleep(300)
        return
    except Exception as e:
        logger.exception(f'execute {patient} failed, {e}')
        return

if __name__ == "__main__":
    patient_list = []
    # read file
    logger.info('start register')
    try:
        with open('patients.json', 'r+') as patient_file:
            patient_list = json.load(patient_file)
        logger.info(f'patient list {patient_list}')
    except Exception as e:
        logger.exception(f'failed to read file, {e}')
        patient_list = []

    if not patient_list:
        logger.error('empty patients, 沒有掛號病人資訊')
        # TODO let user key in by themselves
    
    for p in patient_list:
        # TODO value check
        # start register
        run_on_thread(
            func=execute_register, 
            args=(), 
            kwargs={'patient': p}, 
            daemon=True
        )

    time.sleep(1000)