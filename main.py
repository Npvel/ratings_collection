

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import streamlit as st
import time
import re
import glob, shutil
import os
from pathlib import Path
import datetime
from decimal import *
import sys
from glob import glob
from collections import Iterable
import pandas as pd
import numpy as np

import base64

from io import BytesIO


# chromedriver = webdriver.Chrome(ChromeDriverManager().install())
chromeOptions = webdriver.ChromeOptions()
chromeOptions = webdriver.ChromeOptions()
chromeOptions.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
chromeOptions.add_argument("--headless")
chromeOptions.add_argument("--disable-dev-shm-usage")
chromeOptions.add_argument("--no-sandbox")
browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chromeOptions)




#LOCAL RUN
# prefs = {"download.default_directory" : "C:\Projects\selena\proccesed_files"}
# chromeOptions.add_experimental_option("prefs",prefs)
# chromedriver = r"C:\Projects\rating_for_cb\projects\drivers\chromedriver_win32\chromedriver"
# browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

wait = WebDriverWait(browser, 10)

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
uploaded_file = st.file_uploader("Choose a file")

#if uploaded_file is not None:


# Can be used wherever a "file-like" object is accepted:

dataframe = pd.read_excel(uploaded_file)

st.write(dataframe)


inn_spisok = list(dataframe['INN'].values)
print(inn_spisok)

url_akra = 'https://www.acra-ratings.ru/ratings/issuers/'
url_expert = 'https://www.raexpert.ru/'

# file_folder = glob("./files/*.xls*")
# file_name = file_folder[0].split('\\')[-1]

# for file in file_folder:
#     df_inn = pd.read_excel(file)


time.sleep(30)
ratings_expert = []
dates_expert = []
# ПОИСК ПО ЕКСПЕРТ  

for inn in inn_spisok:
    print(inn)
    time.sleep(2)
    browser.get(url_expert)
    search_fieled = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"input[class='b-search__input']")))
    search_fieled.send_keys(str(inn))

    search_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"button[class='b-search__submit']")))
    search_button.click()
    time.sleep(2)

    try:
        search_results = browser.find_element_by_xpath("//html/body/main/div/div[1]/div/div/div/div[1]/span[2]").text
    # search_results_2 = browser.find_element_by_xpath("//html/body/main/div/div[2]/p").text
    
    # net_result = 'К сожалению ничего найти не удалось. Попробуйте переформулировать Ваш запрос.'
    

        if search_results == '1:': #not 
        
            print('Press button')
            button = browser.find_element_by_css_selector("a[class='b-table__text']")
            button.click()
            
            rating = wait.until(EC.visibility_of_element_located((By.XPATH,"//html/body/main/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[1]/span[1]/span"))).text
            rating_1 = wait.until(EC.visibility_of_element_located((By.XPATH,"//html/body/main/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[2]"))).text
            expert_rating = rating + '_' + rating_1
            print(expert_rating)
            date = browser.find_element_by_xpath("//html/body/main/div/div[2]/div[2]/div/div/table/tbody/tr[1]/td[3]/a").text
            ratings_expert.append(expert_rating)
            dates_expert.append(date)
    
    
    except: #browser.find_element_by_xpath("//html/body/main/div/div[2]/p").text == net_result:

        expert_rating = 'net'
        date = 'net'
        ratings_expert.append(expert_rating)
        dates_expert.append(date)

ratings_akra = []
dates_akra = []
# ПОИСК ПО АКРА
for inn in inn_spisok:
    print(inn)
    time.sleep(2)
    browser.get(url_akra)
    search_fieled = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"input[class='search-input__field']")))
    search_fieled.send_keys(str(inn))
    search_button = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,"button[class='search-input__send-btn']")))
    search_button.click()

    time.sleep(2)
    search_results = browser.find_element_by_css_selector("div[class = 'search-emits__results search-results']").text
    
    print(search_results)
    time.sleep(2)
    
    
    if search_results == 'Найдено: 1':
        time.sleep(2)
        print(search_results)
        rating = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='emits-row__item']/div/p"))).text
        rating_1 = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@class='emits-row__item']/div/span"))).text
        akra_rating = rating + '_' + rating_1
        print(akra_rating)
        ratings_akra.append(akra_rating)
        date = browser.find_element_by_xpath("//html/body/div[2]/div[1]/div/div/div/div[3]/div/div[2]/div[1]/div[1]/div/div/div/div/div[3]/a").text
        print(date)
        dates_akra.append(date)
        # search_fieled.clear()

    elif search_results == 'Найдено: 0':
        # search_fieled.clear()
        akra_rating = 'net'
        date = 'net'
        ratings_akra.append(akra_rating)
        dates_akra.append(date)




df = pd.DataFrame({'INN': inn_spisok,
     'Rating_AKRA': ratings_akra,
     'Date_AKRA': dates_akra,
     'Rating_Expert':ratings_expert,
     'Date_Expert': dates_expert

    })

st.write(df)

def to_excel(df):


    output = BytesIO()

    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Sheet1')

    writer.save()

    processed_data = output.getvalue()

    return processed_data

 

def get_table_download_link(df):

    """Generates a link allowing the data in a given panda dataframe to be downloaded

    in:  dataframe

    out: href string

    """

    val = to_excel(df)

    b64 = base64.b64encode(val)  # val looks like b'...'

    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download csv file</a>' # decode b'abc' => abc

 

df = df # your dataframe

st.markdown(get_table_download_link(df), unsafe_allow_html=True)






