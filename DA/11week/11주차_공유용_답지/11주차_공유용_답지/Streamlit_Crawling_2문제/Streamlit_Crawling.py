import streamlit as st

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
import requests
import time

import pandas as pd

url = 'https://www.seoul.go.kr/main/index.jsp'

st.title('서울특별시 정보수집')

# 
with st.form('form'):
    submit_button_1 = st.form_submit_button('BeautifulSoup - 서울소식 정보 수집')

    if submit_button_1:
            
        html_doc = requests.get(url).text
        soup = BeautifulSoup(html_doc, 'html.parser')
        info_soup = soup.find_all('section', class_ = 'board board2')

        category_list = []
        info_list = []
        url_list = []

        for info in info_soup:
            text_info = info.find('div', class_ = 'txt_area')
            # print(text_info)

            li_info = text_info.find_all('li')
                
            for info_detail in li_info:

                category_list.append(info_detail.find_all('a')[0].text)
                info_list.append(info_detail.find_all('a')[1].text)
                url_list.append(info_detail.find_all('a')[1].get('href')[2:])



            # print('='*20, '수집된 정보 출력 공간입니다.', '='*20)
            # print(category_list)
            # print(info_list)

        tmp_df = pd.DataFrame({'카테고리' : category_list,
                                '제목' : info_list,
                                'url' : url_list})

        print('='*20, '데이터프레임으로 정리한 결과입니다.', '='*20)
        st.write(tmp_df)

with st.form('form2'):

    submit_button_2 = st.form_submit_button('Selenium & BeautifulSoup- 서울소식 이벤트 정보 수집')

    if submit_button_2:

        driver = webdriver.Chrome()
        driver.get(url) 

        time.sleep(3)

        button_info = driver.find_element(By.XPATH, '//*[@id="wrap"]/div[4]/div[1]/section[1]/p/a')
        button_info.click()

        time.sleep(3)

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        tmp = soup.find('div', class_='news-lst')

        title_list = []
        year_list = []
        month_list = []

        tmp = tmp.find_all('a')
        for info in tmp:
            # print(info.find('em', class_='subject').text)
            # print(info.find('em', class_='date').text)
            title_list.append(info.find('em', class_='subject').text)
            year_list.append(info.find('em', class_='date').text.split('-')[0])
            month_list.append(info.find('em', class_='date').text.split('-')[1])

        tmp_df = pd.DataFrame()
        tmp_df['제목'] = title_list
        tmp_df['연도'] = year_list
        tmp_df['월'] = month_list
    
        st.write(tmp_df)
