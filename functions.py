import requests
# from bs4 import BeautifulSoup

import os
import json 
import pandas as pd
import numpy as np 

# import srtm
# import zipfile
# import shutil

import glob
from shutil import copyfile
# import sys 
import time

from datetime import datetime
# from datetime import timedelta
from shutil import copyfile

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

import chromedriver_binary

global_sync = False 

def check_sync(dst_csv):
    global global_sync
    file_last = show_last_file_created('./data/data_pluviometricos/', pattern="*.csv")
    if file_last == '':
        global_sync = True
    else: 
        global_sync = os.path.basename(file_last) == os.path.basename(dst_csv)
    return file_last
    # print('check_sync',global_sync ,  os.path.basename(file_last) , os.path.basename(dst_csv) )



def check_last_state(el='cuenca', val='GTERRA', year=2022):
    global global_sync
    # una vez sincronizado no realizar mas la validacion
    if global_sync == True:
        return True 

    # 2000-Junio-2000-Diciembre-GTERRA-STACUA-PCSAUCE-BORRA.csv.txt
    file_last = show_last_file_created('./data/data_pluviometricos/', pattern="*.txt").replace('.csv.txt','')
    
    # en la primer ejecucion no hay archivos
    if file_last == '':
        return True 

    parts =  file_last.split('-')          
    select_id = {
        'cuenca': 4,
        'subcuenca': 5,
        'estacion': 6,
        'paso': 7,
    }
    # print('validando ', el, 'global_sync',global_sync,  parts[ select_id[el] ],  val, parts)

    # el ultimo procesado fue del 2006 y si estamos en 2007 es un nuevo periodo, 
    if year > int( parts[ 2 ]): 
        global_sync == True
        return True 

    return parts[ select_id[el] ] == val
# -----------------------------------------------------------------------------
def init():
    global dir_root, dir_data, dir_tmp, dir_report, dir_download
    dir_root = os.path.abspath(os.getcwd())
    create_structure()

def create_structure():
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
def my_log(*arguments):
    dt = datetime.now()

    print(dt, *arguments)

    log_file = globals()["dir_tmp"]+'/process.log'
    with open(log_file, 'a') as f:
        print(dt, *arguments, file=f)
            
# -----------------------------------------------------------------------------
def my_sleep(min_sec, max_sec=60):
    time.sleep(np.random.randint(min_sec, max_sec))

# -----------------------------------------------------------------------------
def export_to_csv(data, file_path):
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
    # my_log("Download File .....")
    my_sleep(2,6)
    driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_cmdDescargar").click()  
    # Una vez bajado el archivo da entre 5 a 15 seg para que el archivo se baje y podamos procesarlo
    my_sleep(5,15)

# -----------------------------------------------------------------------------
def get_driver(url, dir_download):
    # dir_download = globals()["dir_download"]

    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : dir_download}
    chromeOptions.add_experimental_option("prefs",prefs)
    # chromedriver = "chromedriver"

    driver = webdriver.Chrome(chrome_options=chromeOptions)

    # Open the main page
    driver.get(url)    
    return driver


# -----------------------------------------------------------------------------
# $x('//*[@id="ctl00_ContentPlaceHolder1_cboCuenca"]')
def get_options_from_select(driver, el_id, types, type):
    xpath = '//*[@id="'+str(el_id)+'"]/option'
    options = driver.find_elements(By.XPATH, xpath)

    eles = {}
    for element in options:
        id = element.get_attribute("value")
        name = element.text
        eles[id] = {'_type': type, 'id': id, 'name': name}
    return { types: eles }


# -----------------------------------------------------------------------------
def show_last_file_created(dir_path, pattern="*"):
    dir = dir_path
    list_of_files = glob.glob(dir+pattern) # * means all if need specific format then *.csv
    latest_file = ''
    if len(list_of_files) > 0  :
        latest_file = max(list_of_files, key=os.path.getctime)
    my_log(" Last File created ", latest_file)   
    return latest_file   



# -----------------------------------------------------------------------------
def drowpdown_select(el_id, option_value, driver):
    xpath = '//*[@id="'+str(el_id)+'"]'
    # my_log('xpath', xpath)
    option = driver.find_element(By.XPATH, xpath)
    val_option = option.get_attribute('text')

    if( val_option != option_value):
        xpath = '//*[@id="'+str(el_id)+'"]/option[. ="'+str(option_value)+'"]'
        # my_log('xpath', xpath)
        option = driver.find_element(By.XPATH, xpath)
        option.click()
        wait = WebDriverWait(driver, 20)
        wait.until(EC.element_to_be_clickable((By.ID, el_id)))   
        my_sleep(3,5)

def drowpdown_select_byvalue(el_id, option_value, driver):
    xpath = '//*[@id="'+str(el_id)+'"]'
    option = driver.find_element(By.XPATH, xpath)
    # my_log('xpath', xpath)
    val_option = option.get_attribute('value')

    if( val_option != option_value):
        xpath = '//*[@id="'+str(el_id)+'"]/option[@value="'+str(option_value)+'"]'
        option = driver.find_element(By.XPATH, xpath)
        option.click()
        my_sleep(3,5)
        # wait = WebDriverWait(driver, 20)
        # wait.until(EC.element_to_be_clickable((By.ID, el_id)))
        my_sleep(3,5) 




# -----------------------------------------------------------------------------
def set_time_filter(params):
    global global_sync
    global_sync = False 

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
def export_json_to_file(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# -----------------------------------------------------------------------------
def process(row, driver, dir_path_ute_csv, dir_path_ute_download):
    # ['cuencas', 'subcuencas', 'estaciones', 'pasos']
    cuencas = get_options_from_select(driver, "ctl00_ContentPlaceHolder1_cboCuenca","cuencas","cuenca")
    for cuenca_id, cuenca  in sorted(cuencas['cuencas'].items()):
        if not check_last_state('cuenca', cuenca_id, row["cboAnioIni"]):
            continue

        my_sleep(1,2)
        drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboCuenca", option_value=cuenca_id, driver=driver)

        my_sleep(1,2)
        subcuencas = get_options_from_select(driver, 'ctl00_ContentPlaceHolder1_cboSubcuenca',"subcuencas","subcuenca")
        cuenca['__subcuencas'] = subcuencas['subcuencas'] 

        for subcuenca_id, subcuenca  in sorted(subcuencas['subcuencas'].items()):
            if not check_last_state('subcuenca', subcuenca_id, row["cboAnioIni"]):
                continue

            my_sleep(1,2)
            drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboSubcuenca", option_value=subcuenca_id, driver=driver)

            my_sleep(1,2)
            estaciones = get_options_from_select(driver, 'ctl00_ContentPlaceHolder1_cboEstacion',"estaciones","estacion")
            subcuenca['__estaciones'] =   estaciones['estaciones']

            for estacion_id, estacion  in sorted(estaciones['estaciones'].items()):
                if not check_last_state('estacion', estacion_id, row["cboAnioIni"]):
                    continue    

                my_sleep(0,1)
                drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboEstacion", option_value=estacion_id, driver=driver)

                pasos = get_options_from_select(driver, 'ctl00_ContentPlaceHolder1_cboPasos',"pasos","paso")
                estacion['__pasos'] =  pasos['pasos']

                for paso_id, paso  in sorted(pasos['pasos'].items()):
                    if not check_last_state('paso', paso_id, row["cboAnioIni"]):
                        continue     

                    my_sleep(1,2)
                    drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboPasos", option_value=paso_id, driver=driver)

                    # my_log("\n----->>>>>>>>Ejecutando",paso_id, estacion_id, subcuenca_id, cuenca_id)
                    dst_csv = dir_path_ute_csv+"/{}-{}-{}-{}-{}-{}-{}-{}.txt".format(
                        row["cboAnioIni"],row["cboMesIni"],row["cboAnioFin"],row["cboMesFin"],
                        cuenca_id, subcuenca_id, estacion_id, paso_id
                    )
                    dst_csv = dst_csv.replace('.txt','.csv')
                    if os.path.exists(dst_csv):
                        my_log('Downloaded', dst_csv)
                        check_sync(dst_csv)
                        continue	
                    # ---------------------------------------------------------
                    # Download
                    # ---------------------------------------------------------
                    my_log('Downloading file: ', dst_csv)
                    download_from_driver(driver)
                    src = show_last_file_created(dir_path_ute_download)
                    copyfile(src, dst_csv+'.txt')
                   
                    # ---------------------------------------------------------
                    # Export to CSV
                    # ---------------------------------------------------------
                    export_raw_to_csv(src, dst_csv)


                    # ---------------------------------------------------------    
                    # partial save
                    # ---------------------------------------------------------
                    export_json_to_file(dir_path_ute_csv+"/partial_{}-{}-{}-{}-ute.json".format(
                        row["cboAnioIni"],row["cboMesIni"],row["cboAnioFin"],row["cboMesFin"]
                    ), cuencas)  
            
    # --------------------------------------------------------------------------
    # Export Structure to Json File
    # --------------------------------------------------------------------------
    export_json_to_file(dir_path_ute_csv+"/{}-{}-{}-{}-ute.json".format(
                        row["cboAnioIni"],row["cboMesIni"],row["cboAnioFin"],row["cboMesFin"]
                    ), cuencas)      


def export_raw_to_csv(file_src, file_to):
    dateparse = lambda x: datetime.strptime(x, '%d/%m/%Y') # %Y-%m-%d %H:%M:%S
    col_names = ['date','hour','cuenca','subcuenca','x1','estacion','nivel','x2','x3']

    df = pd.read_csv(file_src, encoding='ISO-8859-1', 
                names=col_names,sep=";",skiprows=2,
                parse_dates=["date"],date_parser=dateparse)
    df['dt'] = df['date'].astype(str) +' '+ df['hour'].apply(str).str[:-2] +':00:00' # pd.DateOffset(hours=df['hour']/100) #timedelta(2)
    df['dt'] = pd.to_datetime(df['dt'])

    df_obj = df.select_dtypes(['object'])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

    df.drop(['date','hour' ], inplace=True, axis=1)   
    df.to_csv(file_to, index = False) 


