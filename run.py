import functions as fx

from selenium.webdriver.common.by import By

import time, os


# -----------------------------------------------------------------------------
# Initialization
# -----------------------------------------------------------------------------
fx.init()

dir_path_ute_download = fx.dir_download+'data_pluviometricos/'
dir_path_ute_csv = fx.dir_data+'data_pluviometricos/'

os.makedirs(dir_path_ute_download, exist_ok = True) 
os.makedirs(dir_path_ute_csv, exist_ok = True) 

# Setup Driver and main URL
url = "https://apps.ute.com.uy/SgePublico/BajadasGE.aspx"
driver = fx.get_driver(url, dir_path_ute_download)

# -----------------------------------------------------------------------------
# Step 01 - Select "Gestión Embalse" 
# -----------------------------------------------------------------------------
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_optEmbalse").click()
fx.my_sleep(2,3)

# Uncheck "Niveles y Aportes"
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_chkAportes").click()
fx.my_sleep(2,3)

# -----------------------------------------------------------------------------
# Step 02 - Select "Datos Diarios"
# -----------------------------------------------------------------------------
driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_optDiarios").click()   
fx.my_sleep(2,3)

# -----------------------------------------------------------------------------
# Step 03 - Run
# -----------------------------------------------------------------------------

# Setup Month ranges
months = ["Enero","Junio","Diciembre"]

# Setup Years ranges
years = [*range(2000,2021)]

# for testing
# months = ["Enero","Junio"]
# years = [*range(2005,2006)]

for iy, y in enumerate(years):
    fx.my_log('------ Processing Year ', y)
    for im, m in enumerate(months):
        if (im == len(months)-1): 
            continue
        fx.my_log('------\t\t Month ', m, months[im+1])

        # Set Time Filters
        timeParams = {
            "driver": driver,
            "cboAnioIni": y,
            "cboMesIni": m,
            "cboAnioFin": y,
            "cboMesFin": months[im+1]
        }
        fx.set_time_filter(timeParams);

        # Process
        fx.process(timeParams, driver, dir_path_ute_csv, dir_path_ute_download)

 
