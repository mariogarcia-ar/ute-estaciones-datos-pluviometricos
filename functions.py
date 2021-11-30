import requests
from bs4 import BeautifulSoup

import os
import json 
import pandas as pd
import numpy as np 

import srtm
import zipfile
import shutil

import glob
from shutil import copyfile
import sys 
import time

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC


# -----------------------------------------------------------------------------
def init():
    global dir_root, dir_data, dir_tmp, dir_report, dir_download
    dir_root = os.path.abspath(os.getcwd())
    createStructure()

def createStructure():
    globals()["dir_data"] = globals()["dir_root"]+'/data/'
    os.makedirs(globals()["dir_data"], exist_ok = True)

    globals()["dir_tmp"] = globals()["dir_root"]+'/tmp/'
    globals()["dir_download"] = globals()["dir_tmp"]+'/download/'
    os.makedirs(globals()["dir_download"], exist_ok = True)

    globals()["dir_report"] = globals()["dir_root"]+'/report/'
    os.makedirs(globals()["dir_report"], exist_ok = True)

# -----------------------------------------------------------------------------
def file_put_contents(filename, content,mode="w"):
    with open(filename, mode) as f_in: 
        f_in.write(content)

def file_get_contents(filename, mode="r"):
    with open(filename, mode) as f_in: 
        return f_in.read()      

# -----------------------------------------------------------------------------
def exportToCsv(data, file_path):
    ds = pd.DataFrame(data)
    ds.to_csv(file_path, index = False, header = None)

def download(url):
    file_name = os.path.basename(url)
    file_path = globals()["dir_download"]+file_name
    if not os.path.isfile(file_path) :
        r = requests.get(url)  
        file_put_contents(file_path, r.content, "wb")
    return file_path

def download_from_driver(driver):    
    print("Download File .....")
    time.sleep(np.random.randint(2,6))
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_cmdDescargar").click()  
    # TODO: REVISAR EN LA CARPTA DE DESCARGA SI HAY UN ARCHIVO MAS
    time.sleep(np.random.randint(5,15))  




# -----------------------------------------------------------------------------

def getDriver(url, dir_download):
    # dir_download = globals()["dir_download"]

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : dir_download}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromedriver = "chromedriver"

    driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

    # Open the main page
    driver.get(url)    
    return driver


# -----------------------------------------------------------------------------

def getOptionsFromSelect(driver, el_id, types, type):
    xpath = '//*[@id="'+str(el_id)+'"]'
    select_box = driver.find_element(By.XPATH, xpath)
    options = [x for x in select_box.find_elements_by_tag_name("option")]

    eles = {}
    for element in options:
        id = element.get_attribute("value")
        name = element.text
        eles[id] = {'_type': type, 'id': id, 'name': name}
    return { types: eles }


# -----------------------------------------------------------------------------
def showLastFileCreated(dir_path):
    dir = dir_path
    list_of_files = glob.glob(dir+'*') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    # print(latest_file)   
    return latest_file   



# -----------------------------------------------------------------------------



def drowpdown_select(el_id, option_value, driver):
    xpath = '//*[@id="'+str(el_id)+'"]'
    # print('xpath', xpath)
    option = driver.find_element(By.XPATH, xpath)
    val_option = option.get_attribute('text')

    if( val_option != option_value):
        xpath = '//*[@id="'+str(el_id)+'"]/option[. ="'+str(option_value)+'"]'
        # print('xpath', xpath)
        option = driver.find_element(By.XPATH, xpath)
        option.click()
        wait = WebDriverWait(driver, 20)
        wait.until(EC.element_to_be_clickable((By.ID, el_id)))   
        time.sleep(np.random.randint(3,5))  

def drowpdown_select_byvalue(el_id, option_value, driver):
    xpath = '//*[@id="'+str(el_id)+'"]'
    option = driver.find_element(By.XPATH, xpath)
    # print('xpath', xpath)
    val_option = option.get_attribute('value')

    if( val_option != option_value):
        xpath = '//*[@id="'+str(el_id)+'"]/option[@value="'+str(option_value)+'"]'
        option = driver.find_element(By.XPATH, xpath)
        option.click()
        wait = WebDriverWait(driver, 20)
        wait.until(EC.element_to_be_clickable((By.ID, el_id)))  
        time.sleep(np.random.randint(3,5))  




# -----------------------------------------------------------------------------

def setTimeFilter(params):
    # print('setTimeFilter', params)
    driver = params['driver']      
    # ------------------------------------------------------------
    # Filter To Date
    cboAnioFin = params['cboAnioFin'] #'1994'
    cboMesFin = params['cboMesFin'] #'Marzo'

    # //*[@id="ctl00_ContentPlaceHolder1_cboAnioFin"]
    drowpdown_select(el_id="ctl00_ContentPlaceHolder1_cboAnioFin", option_value=cboAnioFin, driver=driver)
    drowpdown_select(el_id="ctl00_ContentPlaceHolder1_cboMesFin", option_value=cboMesFin, driver=driver)


    # ------------------------------------------------------------
    # Filter From Date
    cboAnioIni = params['cboAnioIni'] #'1994'
    cboMesIni = params['cboMesIni'] #'Enero'

    # //*[@id="ctl00_ContentPlaceHolder1_cboAnioIni"]
    drowpdown_select(el_id="ctl00_ContentPlaceHolder1_cboAnioIni", option_value=cboAnioIni, driver=driver)
    drowpdown_select(el_id="ctl00_ContentPlaceHolder1_cboMesIni", option_value=cboMesIni, driver=driver)






# -----------------------------------------------------------------------------


import json
def exportJsonToFile(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



# -----------------------------------------------------------------------------



