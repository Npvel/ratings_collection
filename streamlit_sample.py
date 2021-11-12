import streamlit as st
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains


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
import config
from file_proccessing import owners_file, companies_links, subsid_companies, companies_from_individuals, data_from_files
from dataframe_proccessing import dataframe_create

from utiles1 import ADMIN_COLUMNS,FIN_NAMES,group_company_name, ratios_calculation,BALANCE_RATIOS,\
                    INCOME_RATIOS,TOTAL_FIN_ITEMS,dynamic, final_financial_table, fintable_view, \
                    balance_structure_grath, income_grath, ratios_grath, ccc_graph, subgrades_revenue
    
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
   
ogrn = st.sidebar.text_input('OGRN')
but_1 = st.sidebar.button('hit me')

st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 200px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 200px;
        margin-left: -200px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if but_1:

    # chromedriver = webdriver.Chrome(ChromeDriverManager().install())
    chromeOptions = webdriver.ChromeOptions()
    prefs = {"download.default_directory" : "C:\Projects\selena\proccesed_files"}
    chromeOptions.add_experimental_option("prefs",prefs)
    chromedriver = "C:\Projects\selena\projects\drivers\chromedriver_win32\chromedriver.exe"
    browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

    wait = WebDriverWait(browser, 10)

    def spark_launch(url_not_logged):  #Логин в СПАРК
        browser.get(url_not_logged)
        input_login = browser.find_element_by_css_selector('input[name="username"]')

        input_login.send_keys(config.user_name)

        input_pass = browser.find_element_by_css_selector('input[name="password"]')
        input_pass.send_keys(config.password)

        button_enter = browser.find_element_by_css_selector('button[type="submit"]')
        button_enter.click()

    def search_company(company_code):  #Ввод ОГРН для поиска компании либо ИНН для поиска физюлица или ИП
        
        try:
            
            
            
            button_pop_win = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='modal-content']/div/button[@class='close js-close-btn']")))
            button_pop_win.click()
            print('Нажали кнопку')
        except:
            pass
        print ('НЕ В МОДАЛЕ')
        input_ogrn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[class='form-control search-input js-search-input js-unknown-input js-autocompleted js-immediate-search js-tooltip tt-input']")))
    
        input_ogrn.send_keys(company_code)
        button_search = browser.find_element_by_css_selector('button[title="Поиск"]')
        button_search.click()
        
        company_url = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class='sp-summary__title'] >a"))).get_attribute("href")

        

        return browser.get(company_url)

    
       


    def get_company_reg_data():

        try:

    
            reg_data_button = browser.find_element_by_xpath("//span[text()='Регистрационные данные'] /.. /.. /div")

            reg_data_button.click()
            time.sleep(2)

            okopf = browser.find_element_by_xpath("//table[@class='reg-info-table']/tbody/tr[4]/td[2]").text
            
            okogu = browser.find_element_by_xpath("//table[@class='reg-info-table']/tbody/tr[5]/td[2]").text
            
            okopf = okopf.split(' ')[0]
            okogu = okogu.split(' ')[0]

            return okopf, okogu
        except:
            pass

    def get_company_owner_file():
    
        #Скачиваем excel файл с учредителям
        
        try:
            print('Xpath own')

            owners_data_button = browser.find_element_by_xpath("//span[text()='Совладельцы'] /.. /.. /div")
            print('Scroll before')
            owners_data_button.location_once_scrolled_into_view
            owners_data_button.click()
            print('after click_Xpath')


            excel_file_download_links = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()
        except:
            print("CSS_selector_owner")             #TimeoutException:
            owners_data_button = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[text()='Совладельцы'] /.. /.. /div"))).click()
            owners_data_button.click()
            print('after click CSS')


            excel_file_download_links = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()
           # pass

    def get_company_links_file():
        #Скачиваем excel файл со связями
        try:
            link_data_button = wait.until(EC.visibility_of_element_located((By.XPATH,"//span[text()='Связи компании'] /.. /.. /div"))).click()
            excel_file_download_links = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()
        except TimeoutException:
            pass

    def get_company_subsid_file():

        try:
            subsid_data_button = browser.find_element_by_xpath("//span[text()='Участие в уставном капитале'] /.. /.. /div").click()
            time.sleep(2)
            if not browser.find_element_by_xpath("//div[text()='В доступных источниках нет сведений об участии в уставном капитале']"):
                excel_file_download_subsid = browser.find_element_by_css_selector('button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]').click()
            else:
                pass
        except TimeoutException:
            pass

        # subsid_data_button = wait.until(EC.visibility_of_element_located((By.XPATH,"//span[text()='Участие в уставном капитале'] /.. /.. /div"))).click()
        # excel_file_download_subsid = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()

    def spisok_name():
        time.sleep(5)
        company_name = browser.find_element_by_css_selector("div[class='card-header__title']").text
        company_name = company_name.replace('"','').strip().lower()
        company_name = company_name.replace(' ','_')
        return company_name

    def get_group_list_from_ogrn(ogrn):
        checked_companies_list = []
        to_be_checked_list = []
        to_be_checked_list.append(ogrn)

        for ogrn_company in list(set(to_be_checked_list)):
            if not ogrn in checked_companies_list:
                browser.get('https://spark-interfax.ru/system#/dashboard')
                search_company(ogrn)
                time.sleep(2)
                get_company_owner_file()
                time.sleep(2)
                get_company_links_file()
                time.sleep(2)
                try:
                    time.sleep(2)
                    get_company_subsid_file()
                except:
                    pass
                time.sleep(5)
                checked_companies_list.append(ogrn)

                individuals, companies = data_from_files()
                
        to_be_checked_list.extend(companies)

        
        return checked_companies_list



    def company_file_upload(ogrn):

        browser.get('https://spark-interfax.ru/system#/dashboard')
        search_company(ogrn)
        time.sleep(2)
        print('1')
        
        try:
            time.sleep(2)
            if browser.find_element_by_xpath("//span[text() !='Ликвидировано']") or browser.find_element_by_xpath("//span[text() !='Прекратило деятельность при присоединении']"):
                get_company_reg_data()
                print('2')
                okopf, okogu = get_company_reg_data()
                
            

        # if okogu and okopf:
                if str(okopf[0]) in config.OKOPF and str(okogu[:5]) not in config.OKOGU:
                    time.sleep(2)
                    print('3- Owner file before')
                    get_company_owner_file()
                    time.sleep(5)
                    get_company_links_file()


                    pass
                    time.sleep(5)
                    try:
                        time.sleep(3)
                        get_company_subsid_file()
                        time.sleep(3)
                    except:
                        pass
                    time.sleep(2)
            else:
                time.sleep(5)
                pass
                
        except:
            pass
        

    def individual_file_upload(inn):
        browser.get(f"https://spark-interfax.ru/system/home/card#/physicalperson/inn-{inn}/1")

        time.sleep(2)

        # checked_active = browser.find_element_by_css_selector("input[class='checked switcher__checkbox js-not-print']")
        # checkbox_inactive = browser.find_element_by_css_selector("input[class=switcher__checkbox js-not-print']")
        try:

            if browser.find_element_by_xpath("//div[text()='Актуальных компаний не найдено.']"):
            
                # print('MAKE HISTORY BUTTON')
                browser.find_element_by_css_selector("label[class='switcher js-not-print']").click()
                
                # chekbox_button.location_once_scrolled_into_view
                # chekbox_button.click()
                
                time.sleep(3)
                excel_file_download_inn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()
                
        except:
            time.sleep(5)
            excel_file_download_inn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()

    

    def new_spisok_create(name_company):
        browser.get('https://spark-interfax.ru/system#/dashboard')
        time.sleep(10)
        spiski_menu = wait.until(EC.visibility_of_element_located((By.XPATH,"//*[contains(text(), 'списки')]")))
        browser.execute_script("arguments[0].click();", spiski_menu)

        new_spisok = browser.find_element_by_css_selector("button[class='btn js-not-print btn-sm btn-primary']").click()

        new_spisok_upload = browser.find_element_by_css_selector("input[type=file]")
        
        filePath = f"C:\Projects\selena\{name_company}.txt"
        new_spisok_upload.send_keys(filePath)


        time.sleep(20)

        new_spisok_save_button = browser.find_element_by_css_selector("button[class='btn btn-primary']").click()

    def viborki_file_upload(name_company):
        
        browser.get('https://spark-interfax.ru/system/#/analysis/FIRMS/102571/0')

        time.sleep(15)
        get_spisok = browser.find_element_by_xpath("//div[@class='form-body']/div[@class='form-row']/div[@class='filters-indicator-cell inline-block']/div[@class='relative']/div/div[@class='sp-fake-link inline-block']/button[@class='sp-fake-link dictionary-filter-button']/div[@class='btn__inner']").click()

        time.sleep(15)
        vibor_spiska = browser.find_element_by_xpath(f"//span[text()='{name_company}']").click()
        
        time.sleep(20)
        vibrat_button = browser.find_element_by_css_selector("button[class='btn js-not-print btn-primary pull-right left-offset-10']").click()

        report_button = browser.find_element_by_css_selector("div[class='report-cell vertical-middle']").click()

        time.sleep(20)

        excel_report_download = browser.find_element_by_css_selector("button[class='btn js-not-print btn-primary']").click()

    def flatten(lis):
        for item in lis:
            if isinstance(item, Iterable) and not isinstance(item, str):
                for x in flatten(item):
                    yield x
            else:        
                yield item   




    checked_list = []

    comp_to_check = []
    indiv_to_check = []

    comp_temp = []
    indiv_temp = []

    
    url_logged = 'https://https://spark-interfax.ru/system/#/dashboard/'
    url_not_logged = 'https://spark-interfax.ru/#/dashboard/'
    spark_launch(url_not_logged)
   
    comp_data = ogrn

    company_file_upload(comp_data)
    name_company = spisok_name()
    
    checked_list.append(comp_data)
    
    individuals, companies, no_check_list = data_from_files()
    comp_to_check +=companies
    indiv_to_check +=individuals
    checked_list +=no_check_list

    # print(comp_to_check)
    comp_to_check = list(filter(None, comp_to_check))
    for company in comp_to_check:
        if not company in checked_list:
            print(f"огрн в проверке: {company}")
            company_file_upload(company)

            ind, comp, no_check = data_from_files()
            checked_list.append(company)
            comp_temp +=comp
            indiv_temp +=ind
            checked_list +=no_check
            
    indiv_to_check = list(filter(None, indiv_to_check))
    
    for individ in indiv_to_check:
        
        if not individ in checked_list:
            
            print(f"инвивидуал в проверке: {individ}")
            individual_file_upload(individ)
            time.sleep(5)
            indiv, comp, no_check = data_from_files()
            time.sleep(5)
            checked_list.append(individ)
            comp_temp +=comp
            checked_list +=no_check
            
            

    comp_to_check.clear()
    comp_temp = list(flatten(comp_temp))
    comp_to_check += comp_temp
    comp_temp.clear()
    comp_to_check = list(filter(None, comp_to_check))
    
    for company in comp_to_check:
        if not company in checked_list:
            
            print(f"огрн в проверке: {company}")
            company_file_upload(company)

            ind, comp, no_check = data_from_files()
            checked_list.append(company)
            comp_temp.extend(comp)
            indiv_temp.extend(ind)
            checked_list.extend(no_check)

    indiv_to_check.clear()
    indiv_temp = list(flatten(indiv_temp))
    indiv_to_check += indiv_temp
    indiv_temp.clear()
    indiv_to_check = list(filter(None, indiv_to_check))
    for individ in indiv_to_check:
        if not individ in checked_list:
            # print(f"инвивидуал в проверке: {individ}")
            individual_file_upload(individ)
            time.sleep(5)
            indiv, comp, no_check = data_from_files()
            time.sleep(5)
            checked_list.append(individ)
            comp_temp +=comp
            checked_list +=no_check
    
    viborki_list = comp_temp + checked_list
    viborki_list = list(flatten(viborki_list))
    viborki_list = list(set(viborki_list))

    # print(f"VIBORKI: {len(viborki_list)}")
    # print(viborki_list)
    
    with open(f"{name_company}.txt", "w") as file_txt:
        print(*viborki_list, file=file_txt, sep="\n")

    new_spisok_create(name_company)
    time.sleep(10)
    viborki_file_upload(name_company)

    time.sleep(20)
    

    
    import pandas as pd
    import sys
    import datetime
    from decimal import *
    import numpy as np

    import plotly.offline as py
    import plotly.graph_objects as go
    from plotly.graph_objs import *
    from plotly.offline import iplot
    from plotly.offline import init_notebook_mode, plot_mpl
    py.offline.init_notebook_mode(connected=True)

    from dataframe_proccessing import dataframe_create

   
    spark_df = dataframe_create()

    df_admin = spark_df
    col_names = ADMIN_COLUMNS
    for col_name in col_names:
        if col_name not in df_admin.columns:
            df_admin[col_name] = 0
    df_admin = df_admin[col_names]
    df_admin['Регистрационный номер'] = df_admin['Регистрационный номер'].astype(str).apply(lambda x: x.split('.')[0])

    cols2drop = ['Наименование на английском', 'Краткое наименование', 
                        'Адрес (место нахождения)', 'Руководитель - ФИО', 'Телефон', 'Электронный адрес', 
                        'Сайт в сети Интернет', 'Дата регистрации', 'Возраст компании, лет', 'Дата ликвидации',
                    'Статус', 'Вид деятельности/отрасль', 'ИДО', 'ИФР', 'ИПД', 'Сводный индикатор', 
                    'Сумма незавершенных исков в роли ответчика, тыс. RUB', 'Важная информация',
             'Наименование', 'Код налогоплательщика',  'Мои списки',
             'Совладельцы, Приоритетный'
                ]
    df_findata = (spark_df.drop(cols2drop, axis=1)
            .set_index('Регистрационный номер')
            .stack()
            .reset_index(level=1)
            .rename(columns={'level_1':'name',0:'val'}))

    df_findata[['Год','Наименование']] = \
        (df_findata.pop('name')
        .str.extract(r'(\d{4}),\s*([^,]*?)\s*,'))

    df_findata['Значение'] = pd.to_numeric(df_findata.pop('val'),errors='coerce')
    df_findata = df_findata.reset_index()

    df_findata['Наименование'] = df_findata['Наименование'].replace(FIN_NAMES)

    fin_rows = df_findata.pivot_table(index=['Регистрационный номер', 'Год'], columns=['Наименование'], values=['Значение'], 
                                    fill_value=0).reset_index()

    fin_rows = fin_rows.rename(columns={"Значение":""})

    fin_rows.columns = [t[0] if t[0] else t[1] for t in fin_rows.columns]
    fin_rows.rename(columns={'Регистрационный номер':'OGRN', 'Год':'year'}, inplace=True)


    spark_fin_rows = fin_rows.copy()

    cols = ['OGRN', 'year'] + list(FIN_NAMES.values())

    for col_name in cols:
        if col_name not in spark_fin_rows.columns:
            spark_fin_rows[col_name] = 0
    spark_fin_rows = spark_fin_rows[cols]

    spark_fin_rows['OGRN'] = spark_fin_rows['OGRN'].astype(str).apply(lambda x: x.split('.')[0])

    spark_fin_rows = pd.merge(spark_fin_rows, df_admin[['Регистрационный номер', 'Краткое наименование']], 
                            how='left', left_on='OGRN', right_on='Регистрационный номер')


    spark_fin_rows = spark_fin_rows.drop_duplicates(subset=['OGRN', 'year'], keep='first')

    spark_fin_rows['OGRN'] = spark_fin_rows['OGRN'].astype(str)

    name_group = group_company_name(spark_fin_rows, df_admin)

    spark_fin_rows['Total debt'] = spark_fin_rows['Borrowed funds (long-term)'] + spark_fin_rows['Borrowed funds (short-term)']
    spark_fin_rows = spark_fin_rows.reset_index()

    st.markdown(
        """
        <style>
        [data-testid="stDataframe"][aria-expanded="true"] > div:first-child {
            width: 2000px;
        }
        [data-testid="stDataframe"][aria-expanded="false"] > div:first-child {
            width: 2000px;
            margin-left: -2000px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    spark_fin_rows_2019 = spark_fin_rows[spark_fin_rows['year'] == max(spark_fin_rows['year'])]
    main_companies = spark_fin_rows_2019[['Регистрационный номер', 'Краткое наименование', 'Revenue','Net profit(loss)',
                                        'TOTAL ASSETS','Total debt']].copy()

            
    main_companies = main_companies.sort_values('Revenue', ascending=False)
    main_companies['% of Total Rev'] = main_companies['Revenue'] / main_companies['Revenue'].sum()*100
    main_companies['% of Total Profit'] = main_companies['Net profit(loss)'] / main_companies['Net profit(loss)'].sum()*100
    main_companies['% of Total Assets'] = main_companies['TOTAL ASSETS'] / main_companies['TOTAL ASSETS'].sum()*100
    main_companies['% of Total Debt'] = main_companies['Total debt'] / main_companies['Total debt'].sum()*100
    main_companies = main_companies[(main_companies['% of Total Rev'] >=2) | (main_companies['% of Total Assets'] >=2) | (main_companies['% of Total Debt'] >=2)]
    main_companies = main_companies[['Регистрационный номер', 'Краткое наименование', 'Revenue', '% of Total Rev',
                                    'Net profit(loss)', '% of Total Profit', 'TOTAL ASSETS', '% of Total Assets',
                                    'Total debt', '% of Total Debt']]

    main_companies['Регистрационный номер'] = main_companies['Регистрационный номер'].astype(str).apply(lambda x: x.split('.')[0])
    # main_companies['Revenue'] = main_companies['Revenue'].apply(lambda x: '{:20,.0f}'.format(x))
    # main_companies['TOTAL ASSETS'] = main_companies['TOTAL ASSETS'].apply(lambda x: '{:20,.0f}'.format(x))

    main_companies['% of Total Rev'] = main_companies['% of Total Rev'].apply(lambda x: '{:20,.2f}%'.format(x))
    main_companies['% of Total Profit'] = main_companies['% of Total Profit'].apply(lambda x: '{:20,.2f}%'.format(x))
    main_companies['% of Total Assets'] = main_companies['% of Total Assets'].apply(lambda x: '{:20,.2f}%'.format(x))
    main_companies['% of Total Debt'] = main_companies['% of Total Debt'].apply(lambda x: '{:20,.2f}%'.format(x))

    st.title(f'There are {df_admin.shape[0]} companies in the {name_group} Group structure')
    st.title('The largest companies in the Group:')

    st.dataframe(main_companies.head(30).style.format({"Revenue": "{:,.0f}", "Net profit(loss)":"{:,.0f}",
                                      "TOTAL ASSETS": "{:,.0f}", "Total debt": "{:,.0f}"})\
                                .bar(subset=["Revenue",], color='rgb(129, 238, 238)')\
                                .bar(subset=["Net profit(loss)",], color='lightgreen')\
                                .bar(subset=["TOTAL ASSETS"], color='lightblue')\
                                .bar(subset=["Total debt",], color='rgb(246,135,135)'))

    ratios_rus = spark_fin_rows.apply(ratios_calculation, axis=1)

    max_sales_df = ratios_rus[(ratios_rus['year'] == max(ratios_rus['year']))]

    max_sales_df = max_sales_df[max_sales_df['Revenue'] == max(max_sales_df['Revenue'])]
    company_ogrn = list(max_sales_df['Регистрационный номер'])
                            
    df_fin_analyse = ratios_rus[ratios_rus['Регистрационный номер'].isin(company_ogrn)]
    df_fin_analyse_dynamic = dynamic(df_fin_analyse, TOTAL_FIN_ITEMS)      

    finance_analyse_main_table = final_financial_table(df_fin_analyse,df_fin_analyse_dynamic)

    balance_sa = finance_analyse_main_table['LONG-TERM ASSETS':'TOTAL ASSETS'].copy()
    balance_sa = fintable_view(balance_sa)

    income_sa = finance_analyse_main_table['Revenue':'Net profit(loss)'].copy()
    income_sa = fintable_view(income_sa)

    ratios_sa = finance_analyse_main_table['CFO':'Tangible net worth'].copy()
    ratio_sa = fintable_view(ratios_sa)      

    def color_negative_red(val):
        """
        Takes a scalar and returns a string with
        the css property `'color: red'` for negative
        strings, black otherwise.
        """
        try:
            color = 'red' if val < 0 else 'black'
            return 'color: %s' % color
        except:
            pass

    def highlight_max(s):
        '''
        highlight the maximum in a Series yellow.
        '''
        is_max = s == s.max()
        return ['background-color: yellow' if v else '' for v in is_max]


    import plotly.graph_objects as go

    fig = go.Figure()

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = finance_analyse_main_table.iloc[11,-3],
        title = {"text": "Revenue<br>"},
        number = {'prefix': "€"},
        domain = {'x': [0, 0.5], 'y': [0, 0.5]},
        delta = {'reference': finance_analyse_main_table.iloc[11,-6], 'relative': True, 'position' : "top"}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = finance_analyse_main_table.iloc[18,-3],
        title = {"text": "Net profit(loss)<br>"},
        number = {'prefix': "€"},
        delta = {'reference': finance_analyse_main_table.iloc[18,-6], 'relative': True},
        domain = {'x': [0, 0.5], 'y': [0.5, 1]}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = finance_analyse_main_table.iloc[10,-3],
        title = {"text": "Assets<br>"},
        number = {'prefix': "€"},
        delta = {'reference': finance_analyse_main_table.iloc[10,-6], 'relative': True, 'position' : "top"},
        domain = {'x': [0.6, 1], 'y': [0,0.5]}))

    fig.add_trace(go.Indicator(
        mode = "number+delta",
        value = finance_analyse_main_table.iloc[5,-3],
        title = {"text": "Equity<br>"},
        number = {'prefix': "€"},
        delta = {'reference': finance_analyse_main_table.iloc[5,-6], 'relative': True},
        domain = {'x': [0.6, 1], 'y': [0.5, 1]}))

    # fig.show()
    fig.update_layout(width=800, height=600)
    fig.update_layout(paper_bgcolor = "lightgray")

    st.plotly_chart(fig)

    figure_format={}
    bar_columns = []

    for column in finance_analyse_main_table.columns:
        if '%' in column:
            figure_format[column] = '{:0,.2f}'
        else:
            figure_format[column] = '{:0,.1f}'
            bar_columns.append(column)

    st.title(f"Main company within the Group by sales is {df_fin_analyse['Краткое наименование'].unique()[0]}, OGRN:{df_fin_analyse['OGRN'].unique()[0]}")
    st.title('BALANCE STRUCTURE')
    st.dataframe(finance_analyse_main_table['LONG-TERM ASSETS':'TOTAL ASSETS'].head(40).fillna(0).style.format(figure_format)\
                                        .applymap(color_negative_red)\
                                        .bar(subset=bar_columns, color='lightblue'))

    balance_picture = balance_structure_grath(finance_analyse_main_table)

    st.plotly_chart(balance_picture)

    st.title('INCOME STATEMENT')
    st.dataframe(finance_analyse_main_table['Revenue':'Net profit(loss)'].head(40).fillna(0).style.format(figure_format)\
                                        .applymap(color_negative_red)\
                                        .bar(subset=bar_columns, color='lightblue'))

    income_picture = income_grath(finance_analyse_main_table)
    # st.plotly_chart(income_picture)

    st.title('RATIOS')
    st.dataframe(finance_analyse_main_table['CFO':'Tangible net worth'].head(40).fillna(0).style.format(figure_format)\
                                        .applymap(color_negative_red)\
                                        .bar(subset=bar_columns, color='lightblue'))

    ratios_picture = ratios_grath(finance_analyse_main_table)
    # st.plotly_chart(ratios_picture)

    ccc_picture = ccc_graph(finance_analyse_main_table)

    # st.plotly_chart(ccc_picture)

    rev_list, negatives = subgrades_revenue(finance_analyse_main_table)
    rev_profit = pd.Series(rev_list, name='Revenure & Profitability')
    negative_summary = pd.Series(negatives, name='Negative Summary')

    sub_grades = pd.concat([rev_profit, negative_summary], axis=1)

    sub_grades = sub_grades.melt()

    sub_grades.rename(columns={'variable':'sub_gardes', 'value':'Comments'}, inplace=True)

    sub_grades = sub_grades.dropna()

    sub_grades = sub_grades.groupby(['sub_gardes'])['Comments'].apply(lambda x: ', '.join(x))

    import plotly.graph_objects as go

    values = [['Negative Summary','Revenue & Profitability'],list(sub_grades.values)]

    fig = go.Figure(data=[go.Table(
    columnorder = [1,2],
    columnwidth = [80,400],
    header = dict(
        values = [['<b>Subgrades</b><br>stand-alone'],
                    ['<b>DESCRIPTION</b>']],
        line_color='darkslategray',
        fill_color='royalblue',
        align=['left','center'],
        font=dict(color='white', size=12),
        height=40
    ),
    cells=dict(
        values=values,
        line_color='darkslategray',
        fill=dict(color=['paleturquoise', 'white']),
        align=['left', 'center'],
        font_size=12,
        height=30)
        )
    ])

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        
    )
    fig.update_layout(width=800, height=400)
    
    st.plotly_chart(fig)


    # ADMIN_COLUMNS = ['Регистрационный номер', 'Наименование на английском', 'Краткое наименование', 
    #                         'Адрес (место нахождения)', 'Руководитель - ФИО', 'Телефон', 'Электронный адрес', 
    #                         'Сайт в сети Интернет', 'Дата регистрации', 'Возраст компании, лет', 'Дата ликвидации',
    #                     'Статус', 'Вид деятельности/отрасль', 'ИДО', 'ИФР', 'ИПД', 'Сводный индикатор', 
    #                     'Сумма незавершенных исков в роли ответчика, тыс. RUB', 'Важная информация', 'Совладельцы, Приоритетный']
        
    # df_admin = spark_df
    # col_names = ADMIN_COLUMNS
    # for col_name in col_names:
    #     if col_name not in df_admin.columns:
    #         df_admin[col_name] = 0
    # df_admin = df_admin[col_names]

    # cols2drop = ['Наименование на английском', 'Краткое наименование', 
    #                         'Адрес (место нахождения)', 'Руководитель - ФИО', 'Телефон', 'Электронный адрес', 
    #                         'Сайт в сети Интернет', 'Дата регистрации', 'Возраст компании, лет', 'Дата ликвидации',
    #                     'Статус', 'Вид деятельности/отрасль', 'ИДО', 'ИФР', 'ИПД', 'Сводный индикатор', 
    #                     'Сумма незавершенных исков в роли ответчика, тыс. RUB', 'Важная информация',
    #             'Наименование', 'Код налогоплательщика', 'Мои списки',
    #             'Совладельцы, Приоритетный'
    # ]

    # df_findata = (spark_df.drop(cols2drop, axis=1)
    #         .set_index('Регистрационный номер')
    #         .stack()
    #         .reset_index(level=1)
    #         .rename(columns={'level_1':'name',0:'val'}))


    # df_findata[['Год','Наименование']] = \
    #     (df_findata.pop('name')
    #     .str.extract(r'(\d{4}),\s*([^,]*?)\s*,'))



    # df_findata['Значение'] = pd.to_numeric(df_findata.pop('val'),errors='coerce')
    # df_findata = df_findata.reset_index()

    # FILE = {'Нематериальные активы':'Intangible assets', 'Основные средства': 'Capital assets',
    #         'Долгосрочные финансовые вложения': 'Long-term investments',
    #         'Отложенные налоговые активы':'Deferred tax asset','Прочие внеоборотные активы':'Other long-term assets', 
    #         'Внеоборотные активы':'LONG-TERM ASSETS','Запасы':'Inventory','НДС по приобретенным ценностям':'VAT on inventory', 
    #         'Дебиторская задолженность':'Accounts receivable', 'Краткосрочные финансовые вложения':'Short-term investments',
    #         'Денежные средства и денежные эквиваленты':'Cash and cash equivalents',
    #         'Прочие краткосрочные обязательства':'Other current assets', 'Оборотные активы':'CURRENT ASSETS',
    #         'Уставный капитал':'Charter capital', 'Добавочный капитал':'Paid-in capital',
    #         'Резервный капитал':'Reserved capital','Нераспределенная прибыль (непокрытый убыток)':'Retained earnings for reporting year',
    #         'Капитал и резервы':'CAPITAL AND RESERVES','Заёмные средства (долгосрочные)': 'Borrowed funds (long-term)',
    #         'Отложенные налоговые обязательства':'Deferred tax liabilities','Прочие долгосрочные обязательства':'Other long-term liabilities',
    #         'Долгосрочные обязательства':'LONG-TERM LIABILITIES','Заёмные средства (краткосрочные)':'Borrowed funds (short-term)',
    #         'Кредиторская задолженность':'Accounts payable','Прочие краткосрочные обязательства':'Other short-term liabilities',
    #         'Краткосрочные обязательства':'CURRENT LIABILITIES',
    #         'Выручка':'Revenue','Себестоимость продаж':'Cost of sales','Валовая прибыль (убыток)':'Gross profit (loss)',
    #         'Коммерческие расходы':'Selling expenses','Управленческие расходы':'Administrative expenses',
    #         'Прибыль (убыток) от продажи':'Operating profit (loss)','Проценты к получению':'Interest income',
    #         'Проценты к уплате':'Interest expense','Прочие доходы':'Other income','Прочие расходы':'Other expenses',
    #         'Прибыль (убыток) до налогообложения':'Pre-tax profit (loss)','Текущий налог на прибыль':'Profit tax',
    #         'Чистая прибыль (убыток)':'Net profit(loss)', 'Активы  всего':'TOTAL ASSETS', 'Чистые активы':'Net assets',
    #     'Пассивы всего':'TOTAL LIABILITIES', 'Сальдо денежных потоков от текущих операций': 'CFO'}

    # df_findata['Наименование'] = df_findata['Наименование'].replace(FILE)

    # fin_rows = df_findata.pivot_table(index=['Регистрационный номер', 'Год'], columns=['Наименование'], values=['Значение'], 
    #                                 fill_value=0).reset_index()

    # fin_rows = fin_rows.rename(columns={"Значение":""})
    # #fin_rows.set_index(['OGRN', 'year'])
    # fin_rows.columns = [t[0] if t[0] else t[1] for t in fin_rows.columns]
    # fin_rows.rename(columns={'Регистрационный номер':'OGRN', 'Год':'year'}, inplace=True)

    # spark_fin_rows = fin_rows.copy()

    # cols = ['OGRN', 'year'] + list(FILE.values())

    # for col_name in cols:
    #     if col_name not in spark_fin_rows.columns:
    #         spark_fin_rows[col_name] = 0
    # spark_fin_rows = spark_fin_rows[cols]


    # spark_fin_rows = pd.merge(spark_fin_rows, df_admin[['Регистрационный номер', 'Краткое наименование']], 
    #                         how='left', left_on='OGRN', right_on='Регистрационный номер')


    # spark_fin_rows = spark_fin_rows.drop_duplicates(subset=['OGRN', 'year'], keep='first')

    # year = max(spark_fin_rows['year'])
    # date_max = f"{year}-12-31"
    # #date = "2018-12-31"
    # # print(date_max)

    # spark_fin_rows['Gross debt'] = spark_fin_rows['Borrowed funds (long-term)'] + spark_fin_rows['Borrowed funds (short-term)']
    # spark_fin_rows = spark_fin_rows.reset_index()

    # spark_fin_rows['Total debt'] = spark_fin_rows['Borrowed funds (long-term)'] + spark_fin_rows['Borrowed funds (short-term)']
    # spark_fin_rows = spark_fin_rows.reset_index()


    # spark_fin_rows_2019 = spark_fin_rows[spark_fin_rows['year'] == max(spark_fin_rows['year'])]
    # main_companies = spark_fin_rows_2019[['Регистрационный номер', 'Краткое наименование', 'Revenue', 'TOTAL ASSETS', 'Total debt']].copy()
    # main_companies = main_companies.sort_values('Revenue', ascending=False)
    # main_companies['% of Total Rev'] = main_companies['Revenue'] / main_companies['Revenue'].sum()*100
    # main_companies['% of Total Assets'] = main_companies['TOTAL ASSETS'] / main_companies['TOTAL ASSETS'].sum()*100
    # main_companies['% of Total Debt'] = main_companies['Total debt'] / main_companies['Total debt'].sum()*100
    # main_companies = main_companies[(main_companies['% of Total Rev'] >=2) | (main_companies['% of Total Assets'] >=2) | (main_companies['% of Total Debt'] >=2)]
    # main_companies = main_companies[['Регистрационный номер', 'Краткое наименование', 'Revenue', '% of Total Rev',
    #                                 'TOTAL ASSETS', '% of Total Assets', 'Total debt', '% of Total Debt']]


    # main_companies['Регистрационный номер'] = main_companies['Регистрационный номер'].astype(str).apply(lambda x: x.split('.')[0])
    # # main_companies['Revenue'] = main_companies['Revenue'].apply(lambda x: '{:20,.0f}'.format(x))
    # # main_companies['TOTAL ASSETS'] = main_companies['TOTAL ASSETS'].apply(lambda x: '{:20,.0f}'.format(x))

    # main_companies['% of Total Rev'] = main_companies['% of Total Rev'].apply(lambda x: '{:20,.2f}%'.format(x))
    # main_companies['% of Total Assets'] = main_companies['% of Total Assets'].apply(lambda x: '{:20,.2f}%'.format(x))
    # main_companies['% of Total Debt'] = main_companies['% of Total Debt'].apply(lambda x: '{:20,.2f}%'.format(x))

    # st.dataframe(main_companies.head(30).style.format({"Revenue": "{:,.0f}", 
    #                         "TOTAL ASSETS": "{:,.0f}",\
    #                         "Total debt": "{:,.0f}"})\
    #                 .bar(subset=["Revenue",], color='lightgreen')\
    #                 .bar(subset=["TOTAL ASSETS"], color='lightblue')\
    #                 .bar(subset=["Total debt",], color='rgb(246,135,135)'))


    # st.markdown(
    #     """
    #     <style>
    #     [data-testid="stDataframe"][aria-expanded="true"] > div:first-child {
    #         width: 2000px;
    #     }
    #     [data-testid="stDataframe"][aria-expanded="false"] > div:first-child {
    #         width: 2000px;
    #         margin-left: -2000px;
    #     }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )

    # def ratios_calculation(df):
        
    #     df['NWS'] = df['CURRENT ASSETS'] - df['CURRENT LIABILITIES']
    #     if df['CURRENT LIABILITIES'] != 0:
    #         df['CL'] = df['CURRENT ASSETS'] / df['CURRENT LIABILITIES']
    #         df['QR'] = (df['CURRENT ASSETS'] - df['Inventory']) / df['CURRENT LIABILITIES']
            
    #     if df['Revenue'] !=0:
    #         df['DSO, days'] = df['Accounts receivable'] /  df['Revenue'] * 365
    #         df['DEBT/SALES'] = (df['Borrowed funds (long-term)'] + df['Borrowed funds (short-term)']) / df['Revenue']
    #         df['Gross margin'] = df['Gross profit (loss)'] / df['Revenue']
    #         df['EBIT margin'] = (df['Pre-tax profit (loss)'] + df['Interest expense'] - df['Interest income']) / df['Revenue']
    #         df['Net profitability'] = df['Net profit(loss)'] / df['Revenue']
            
    #     if df['Cost of sales'] !=0:
    #         df['DIO, days'] = df['Inventory'] / df['Cost of sales']*365
    #         df['DPO, days'] = df['Accounts payable'] / df['Cost of sales']*365
        
        
    #     if df['TOTAL ASSETS'] != 0:
    #         df['ER'] = df['CAPITAL AND RESERVES'] / df['TOTAL ASSETS']
    #     if df['CAPITAL AND RESERVES'] != 0:
    #         df['FIN_GEARING'] = (df['Borrowed funds (long-term)'] + df['Borrowed funds (short-term)'])/df['CAPITAL AND RESERVES']
    #     if (df['Pre-tax profit (loss)'] + df['Interest expense'] - df['Interest income']) !=0:
    #         df['DEBT/EBIT'] = (df['Borrowed funds (long-term)'] + df['Borrowed funds (short-term)']) / \
    #                 (df['Pre-tax profit (loss)'] + df['Interest expense'] - df['Interest income'])
    #     if df['Interest expense'] != 0:
    #         df['ICR'] = (df['Operating profit (loss)']) / \
    #                 df['Interest expense']
    #     else:
    #         df['ICR'] = 0
        
    #     if df['TOTAL ASSETS'] != 0:
    #         df['Debt/Total Assets'] = (df['Borrowed funds (long-term)'] + df['Borrowed funds (short-term)']) / df['TOTAL ASSETS']
        
            
    #     return df



    # ratios_rus = spark_fin_rows.apply(ratios_calculation, axis=1)
    # ratios_rus['CCC'] = ratios_rus['DSO, days'] + ratios_rus['DIO, days'] - ratios_rus['DPO, days']

    # ratios_rus['year'] = pd.to_numeric(ratios_rus['year'])


    # ratios_rus['Cahs&short_investment'] = ratios_rus['Cash and cash equivalents'] + ratios_rus['Short-term investments']
    # ratios_rus['Gross_debt'] = ratios_rus['Borrowed funds (long-term)'] + ratios_rus['Borrowed funds (short-term)']
    # ratios_rus['Liabilities'] = ratios_rus['LONG-TERM LIABILITIES'] + ratios_rus['CURRENT LIABILITIES']


    # max_sales_df = ratios_rus[(ratios_rus['year'] == max(ratios_rus['year']))]

    # max_sales_df = max_sales_df[max_sales_df['Revenue'] == max(max_sales_df['Revenue'])]
    # company_ogrn = list(max_sales_df['Регистрационный номер'])
                            
    # df_fin_analyse = ratios_rus[ratios_rus['Регистрационный номер'].isin(company_ogrn)]


    # df_fin_analyse = df_fin_analyse[['year', 'Краткое наименование','Регистрационный номер', 'LONG-TERM ASSETS', 
    #                                 'Inventory', 'Accounts receivable', 'Cahs&short_investment','CURRENT ASSETS',
    #                                 'CAPITAL AND RESERVES', 'Borrowed funds (long-term)','Borrowed funds (short-term)',
    #                                 'Accounts payable', 'CURRENT LIABILITIES','TOTAL ASSETS','Revenue',
    #                                 'Gross profit (loss)', 'Cost of sales', 'Operating profit (loss)',
    #                                 'Interest income','Interest expense', 'Pre-tax profit (loss)', 
    #                                 'Net profit(loss)', 'CFO', 'CL', 'QR', 'NWS', 'DIO, days', 'DPO, days',
    #                                 'DSO, days', 'CCC', 'Gross_debt', 'ER', 'FIN_GEARING',  'ICR', 
    #                                 'DEBT/EBIT', 'DEBT/SALES','Debt/Total Assets']].copy()

    # df_fin_analyse_dynamic = (df_fin_analyse[['Регистрационный номер', 'Краткое наименование', "year"]]
    #                     .join(df_fin_analyse
    #                     .groupby(['Регистрационный номер', 'Краткое наименование'], as_index=False)
    #                     [['LONG-TERM ASSETS','Inventory', 'Accounts receivable', 'Cahs&short_investment','CURRENT ASSETS',
    #                         'CAPITAL AND RESERVES', 'Borrowed funds (long-term)','Borrowed funds (short-term)',
    #                         'Accounts payable', 'CURRENT LIABILITIES','TOTAL ASSETS','Revenue','Gross profit (loss)', 
    #                         'Cost of sales', 'Operating profit (loss)','Interest income','Interest expense', 
    #                         'Pre-tax profit (loss)', 'Net profit(loss)', 'CFO', 'CL', 'QR', 'NWS', 'DIO, days', 'DPO, days',
    #                         'DSO, days', 'CCC', 'Gross_debt', 'ER', 'FIN_GEARING',  'ICR', 'DEBT/EBIT', 'DEBT/SALES',
    #                         'Debt/Total Assets']]
    #                     .apply(lambda x: x.diff()/x.shift().abs()*100)))



    # df_fin_analyse = df_fin_analyse.T
    # df_fin_analyse.columns = df_fin_analyse.loc['year']
    # df_fin_analyse = df_fin_analyse.drop('year')

    # df_fin_analyse_dynamic = df_fin_analyse_dynamic.T
    # df_fin_analyse_dynamic.columns = df_fin_analyse_dynamic.loc['year']
    # df_fin_analyse_dynamic = df_fin_analyse_dynamic.drop('year')

    # df_merged = df_fin_analyse.join(df_fin_analyse_dynamic, rsuffix='_%')

    # cols = [str(x) for x in list(df_merged)]

    # cols = sorted(cols)
    # df_merged = df_merged[cols]


    # df_merged_ratio = df_merged.reindex(['Краткое наименование', 'Регистрационный номер', 'CFO', 'CL', 'QR', 'NWS',
    #                                     'DIO, days', 'DPO, days', 'DSO, days', 'CCC', 'Gross_debt','ER','FIN_GEARING', 
    #                                     'ICR', 'DEBT/EBIT', 'DEBT/SALES', 'Debt/Total Assets'])

    # df_merged_fin = df_merged.reindex(['LONG-TERM ASSETS', 'Inventory', 'Accounts receivable','Cahs&short_investment',
    #                                 'CURRENT ASSETS', 'CAPITAL AND RESERVES', 'Borrowed funds (long-term)',
    #                                 'Borrowed funds (short-term)', 'Accounts payable', 'CURRENT LIABILITIES','TOTAL ASSETS',
    #                                 'Revenue', 'Gross profit (loss)', 'Cost of sales', 'Operating profit (loss)','Interest income', 
    #                                 'Interest expense', 'Pre-tax profit (loss)', 'Net profit(loss)'])

    # idx1 = "TOTAL ASSETS"
    # idx2 = "Revenue"

    # balance = df_merged_fin.iloc[:(df_merged_fin.index == idx1).argmax()]
    # income = df_merged_fin.iloc[(df_merged_fin.index == idx2).argmax() + 1:]

    # cols = df_merged_fin.columns[~df_merged_fin.columns.str.contains(r"%")]

    # r1 = balance[cols] / df_merged_fin.loc[idx1, cols].replace(0, 0.01) * 100
    # r2 = income[cols] / df_merged_fin.loc[idx2, cols].replace(0, 0.01) * 100

    # res = (pd
    #     .concat(
    #         [r1.append(pd.Series([100] * len(cols), index=cols, name=idx1)),
    #         r2.append(pd.Series([100] * len(cols), index=cols, name=idx2))])
    #     .add_suffix("%sh"))
    # res = pd.concat([df_merged_fin, res], axis=1)

    # cols = [str(x) for x in list(res)]
    # cols = sorted(cols)

    # res = res[cols]


    # finance_analyse_main_table = pd.concat([res,df_merged_ratio])

    # finance_analyse_main_table_name = (finance_analyse_main_table
    #                             .reindex(['Краткое наименование','Регистрационный номер','LONG-TERM ASSETS', 'Inventory',
    #                                         'Accounts receivable','Cahs&short_investment','CURRENT ASSETS', 
    #                                         'CAPITAL AND RESERVES', 'Borrowed funds (long-term)','Borrowed funds (short-term)',
    #                                         'Accounts payable', 'CURRENT LIABILITIES','TOTAL ASSETS','Revenue', 'Gross profit (loss)',
    #                                         'Cost of sales', 'Operating profit (loss)','Interest income', 'Interest expense', 
    #                                         'Pre-tax profit (loss)', 'Net profit(loss)','CFO', 'CL', 'QR', 'NWS', 'DIO, days',
    #                                         'DPO, days', 'DSO, days', 'CCC','Gross_debt', 'ER', 'FIN_GEARING',  'ICR', 
    #                                         'DEBT/EBIT', 'DEBT/SALES','Debt/Total Assets']))

    # finance_analyse_main_table = (finance_analyse_main_table
    #                             .reindex(['LONG-TERM ASSETS', 'Inventory','Accounts receivable','Cahs&short_investment',
    #                                         'CURRENT ASSETS','CAPITAL AND RESERVES', 'Borrowed funds (long-term)',
    #                                         'Borrowed funds (short-term)','Accounts payable', 'CURRENT LIABILITIES',
    #                                         'TOTAL ASSETS','Revenue', 'Cost of sales', 'Gross profit (loss)',
    #                                         'Operating profit (loss)','Interest income', 'Interest expense', 
    #                                         'Pre-tax profit (loss)', 'Net profit(loss)','CFO', 'CL', 'QR', 'NWS',
    #                                         'DIO, days','DPO, days', 'DSO, days', 'CCC','Gross_debt', 'ER', 'FIN_GEARING',
    #                                         'ICR', 'DEBT/EBIT', 'DEBT/SALES','Debt/Total Assets']))

    # assets_2019 = finance_analyse_main_table.loc['LONG-TERM ASSETS':'CURRENT ASSETS', finance_analyse_main_table.columns[-5]]
    # liabilit_2019 = finance_analyse_main_table.loc['CAPITAL AND RESERVES':'CURRENT LIABILITIES', finance_analyse_main_table.columns[-5]]

    # Assets = list(finance_analyse_main_table['LONG-TERM ASSETS':'CURRENT ASSETS'].index)
    # Liabilities = list(finance_analyse_main_table['CAPITAL AND RESERVES':'CURRENT LIABILITIES'].index)

    # # py.sign_in('username', 'api_key')
    # trace1 = {
    # "name": "LONG-TERM ASSETS", 
    # "type": "bar", 
    # "x": ["Assets"], 
    # "y": [assets_2019.loc['LONG-TERM ASSETS']/100], 
    # "marker": {"color": "rgb(0,60,118)"}, "text": "Long-term assets", "textposition":'inside'
    # }
    # trace2 = {
    # "name": "Inventory", 
    # "type": "bar", 
    # "x": ["Assets"], 
    # "y": [assets_2019.loc['Inventory']/100], 
    # "marker": {"color": "rgb(0,94,184)"}, "text": "Inventory", "textposition":'inside'
    # }
    # trace3 = {
    # "name": "Accounts receivable", 
    # "type": "bar", 
    # "x": ["Assets"], 
    # "y": [assets_2019.loc['Accounts receivable']/100], 
    # "marker": {"color": "rgb(92,152,209)"}, "text": "Accounts receivables", "textposition":'inside'
    # }
    # trace4 = {
    # "name": "Cahs&short_investment", 
    # "type": "bar", 
    # "x": ["Assets"], 
    # "y": [assets_2019.loc['Cahs&short_investment']/100], 
    # "marker": {"color": "rgb(189,213,236)"}, "text": "Cash&short investment", "textposition":'inside'
    # }

    # trace5 = {
    # "name": "CAPITAL AND RESERVES", 
    # "type": "bar", 
    # "x": ["Liabilities & Equity"], 
    # "y": [liabilit_2019.loc['CAPITAL AND RESERVES']/100], 
    # "marker": {"color": "rgb(69,117,37)"}, "text": "Equity", "textposition":'inside'
    # }
    # trace6 = {
    # "name": "Borrowed funds (long-term)", 
    # "type": "bar", 
    # "x": ["Liabilities & Equity"], 
    # "y": [liabilit_2019.loc['Borrowed funds (long-term)']/100], 
    # "marker": {"color": "rgb(67,176,32)"}, "text": "Loans long-term", "textposition":'inside'
    # }
    # trace7 = {
    # "name": "Borrowed funds (short-term)", 
    # "type": "bar", 
    # "x": ["Liabilities & Equity"], 
    # "y": [liabilit_2019.loc['Borrowed funds (short-term)']/100], 
    # "marker": {"color": "rgb(67,176,42)"}, "text": "Loans short-term", "textposition":'inside'
    # }
    # trace8 = {
    # "name": "Accounts payable", 
    # "type": "bar", 
    # "x": ["Liabilities & Equity"], 
    # "y": [liabilit_2019.loc['Accounts payable']/100], 
    # "marker": {"color": "rgb(162,234,66)"}, "text": "Accounts payable", "textposition":'inside'
    # }

    # data = Data([trace1, trace2, trace3, trace4, trace5, trace6, trace7, trace8])
    # layout = {
    # "title": "Balance Sheet Composition, Percent of Assets, 2016", 
    # "yaxis": {"tickformat": "%"}, 
    # "barmode": "stack"
    # }
    # fig = Figure(data=data, layout=layout)
    # # plot_url = py.plot(fig, filename = f'{file_name}_balance_structure.html')

    # fig.update_layout(width=800, height=600)
    # fig.update_layout(plot_bgcolor='rgba(246,249,253)')

    # st.plotly_chart(fig)

    # fig.update_traces()
    # f = go.FigureWidget(fig)
    # f

    def get_beneficiary_list():

        number_td = browser.find_elements_by_xpath("//table[@class='sp-properties-form sp-properties-form_compact']/tbody/tr")
        number_td = len(number_td)

        time.sleep(2)

        beneficiar = browser.find_element_by_xpath(f"//table[@class='sp-properties-form sp-properties-form_compact']/tbody/tr[{number_td}]/td[1]").text
        

        if beneficiar == 'Бенефициар':
            beneficiar_href = browser.find_element_by_xpath(f"//table[@class='sp-properties-form sp-properties-form_compact']/tbody/tr[{number_td}]/td[2]/a").get_attribute('href')
            browser.get(beneficiar_href)

            beneficiary_inn = browser.find_element_by_xpath("//table[@class='sp-properties-form']/tbody/tr[2]/td[2]").text
            time.sleep(2)

            excel_file_download_beneficiar = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR,'button[class="btn js-not-print btn-sm btn_icon t-export-to-excel-button"]'))).click()

            return beneficiary_inn