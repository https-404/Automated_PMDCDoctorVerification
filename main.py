import re
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def validate_registration_number(reg_num):
    """
    Validate the registration number format: xxxxx-x
    Where xxxxx are digits and x is a letter (either uppercase or lowercase).
    """
    pattern = re.compile(r'^\d{6}-[A-Za-z]$')
    return pattern.match(reg_num) is not None

def check_registration_number(reg_num):
    """
    Check the registration number on the PMC website and return the result as JSON.
    """
    url = 'https://www.pmc.gov.pk/Doctors/Search'
    options = Options()
    options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for the page to load

        # Locate the input field and submit the form
        input_element = driver.find_element(By.ID, 'regist_no')
        input_element.send_keys(reg_num)
        input_element.send_keys(Keys.RETURN)
        
        time.sleep(3)  # Wait for the results to load

        # Extract relevant information
        doctor_info = {}
        rows = driver.find_elements(By.CSS_SELECTOR, '#tBody tr')
        
        if rows:
            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                if len(cols) >= 5:  # Ensure there are enough columns
                    if cols[1].text.strip() == reg_num:
                        doctor_info['registration_number'] = cols[1].text.strip()
                        doctor_info['name'] = cols[2].text.strip()
                        doctor_info['father_name'] = cols[3].text.strip()
                        doctor_info['status'] = cols[4].text.strip()
                        break
                else:
                    print(f"Skipping row with insufficient columns: {len(cols)}")
            if not doctor_info:
                doctor_info['error'] = 'Doctor details not found'
        else:
            doctor_info['error'] = 'No data found'

        return json.dumps(doctor_info)
    except Exception as e:
        return json.dumps({'error': str(e)})
    finally:
        driver.quit()

if __name__ == "__main__":
    reg_num = input("Enter the doctor's registration number: ").strip()
    
    if validate_registration_number(reg_num):
        result = check_registration_number(reg_num)
        print(result)
    else:
        print(json.dumps({'error': 'Invalid registration number format'}))
