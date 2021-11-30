import functions as fx

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC

import time, os
from datetime import datetime
from datetime import timedelta
import numpy as np
import pandas as pd
from shutil import copyfile

# -----------------------------------------------------------------------------
# Inicializamos la estructura de carpetas
fx.init()


dir_path_ute_download = fx.dir_download+'data_pluviometricos/'
dir_path_ute_csv = fx.dir_data+'data_pluviometricos/'

os.makedirs(dir_path_ute_download, exist_ok = True) 
os.makedirs(dir_path_ute_csv, exist_ok = True) 


url = "https://apps.ute.com.uy/SgePublico/BajadasGE.aspx"
driver = fx.getDriver(url, dir_path_ute_download)

driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_optEmbalse").click()
time.sleep(2)
# daily report #19
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_chkAportes").click()
time.sleep(2)
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_optDiarios").click()   
time.sleep(2)


# -----------------------------------------------------------------------------
def process(row):
    # ['cuencas', 'subcuencas', 'estaciones', 'pasos']
    cuencas = fx.getOptionsFromSelect(driver, "ctl00_ContentPlaceHolder1_cboCuenca","cuencas","cuenca")
    for cuenca_id, cuenca  in sorted(cuencas['cuencas'].items()):

        time.sleep(np.random.randint(1,2))
        fx.drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboCuenca", option_value=cuenca_id, driver=driver)

        time.sleep(np.random.randint(1,2))
        subcuencas = fx.getOptionsFromSelect(driver, 'ctl00_ContentPlaceHolder1_cboSubcuenca',"subcuencas","subcuenca")
        cuenca['__subcuencas'] = subcuencas['subcuencas'] 

        for subcuenca_id, subcuenca  in sorted(subcuencas['subcuencas'].items()):
            time.sleep(np.random.randint(1,2))
            fx.drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboSubcuenca", option_value=subcuenca_id, driver=driver)

            time.sleep(np.random.randint(1,2))
            estaciones = fx.getOptionsFromSelect(driver, 'ctl00_ContentPlaceHolder1_cboEstacion',"estaciones","estacion")
            subcuenca['__estaciones'] =   estaciones['estaciones']

            for estacion_id, estacion  in sorted(estaciones['estaciones'].items()):
                time.sleep(np.random.randint(0,1))
                fx.drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboEstacion", option_value=estacion_id, driver=driver)

                pasos = fx.getOptionsFromSelect(driver, 'ctl00_ContentPlaceHolder1_cboPasos',"pasos","paso")
                estacion['__pasos'] =  pasos['pasos']

                for paso_id, paso  in sorted(pasos['pasos'].items()):
                    time.sleep(np.random.randint(1,2))
                    fx.drowpdown_select_byvalue(el_id="ctl00_ContentPlaceHolder1_cboPasos", option_value=paso_id, driver=driver)

                    # print("\nEjecutando",paso, estacion, subcuenca, cuenca)

                    dst_csv = dir_path_ute_csv+"/{}-{}-{}-{}-{}-{}-{}-{}.txt".format(
                        row["cboAnioIni"],row["cboMesIni"],row["cboAnioFin"],row["cboMesFin"],
                        cuenca_id, subcuenca_id, estacion_id, paso_id
                    )
                    dst_csv = dst_csv.replace('.txt','.csv')
                    if os.path.exists(dst_csv):
                        print('Proccesed', dst_csv)
                        continue


                    print('new', dst_csv)
                    fx.download_from_driver(driver)
                    src = fx.showLastFileCreated(dir_path_ute_download)
                    # copyfile(src, dst)
                   
                    exportRawToCsv(src, dst_csv)
            
    fx.exportJsonToFile(fx.dir_data+"/{}-{}-{}-{}-ute.json".format(
                        row["cboAnioIni"],row["cboMesIni"],row["cboAnioFin"],row["cboMesFin"]
                    ), cuencas)      


dateparse = lambda x: datetime.strptime(x, '%d/%m/%Y') # %Y-%m-%d %H:%M:%S
col_names = ['date','hour','cuenca','subcuenca','x1','estacion','nivel','x2','x3']

def exportRawToCsv(file_src, file_to):
    df = pd.read_csv(file_src, encoding='ISO-8859-1', 
                names=col_names,sep=";",skiprows=2,
                parse_dates=["date"],date_parser=dateparse)
    df['dt'] = df['date'].astype(str) +' '+ df['hour'].apply(str).str[:-2] +':00:00' # pd.DateOffset(hours=df['hour']/100) #timedelta(2)
    df['dt'] = pd.to_datetime(df['dt'])

    df_obj = df.select_dtypes(['object'])
    df[df_obj.columns] = df_obj.apply(lambda x: x.str.strip())

    df.drop(['date','hour' ], inplace=True, axis=1)   
    df.to_csv(file_to, index = False) 

# -----------------------------------------------------------------------------
# months = ["Enero","Junio","Diciembre"]
# years = [*range(2000,2021)]

months = ["Enero","Junio"]
years = [*range(2005,2006)]

for iy, y in enumerate(years):
    print('------ Init Year ', y)
    for im, m in enumerate(months):
        if (im == len(months)-1): 
            continue
        print('------ Init Month ', m)
        timeParams = {
            "driver": driver,
            "cboAnioIni": y,
            "cboMesIni": m,
            "cboAnioFin": y,
            "cboMesFin": months[im+1]
        }
        fx.setTimeFilter(timeParams);

        process(timeParams)

 
