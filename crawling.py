# !pip install requests beautifulsoup4
# !pip install selenium
# !pip install sqlalchemy

# ! pip install webdriver-manager
# ! apt install chromium-chromedriver
# ! pip install tqdm

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine, Table, Column, String, MetaData
from selenium.webdriver.chrome.service import Service
import time

from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
import pandas as pd
from selenium.webdriver.chrome.options import Options

from datetime import datetime
import re
from tqdm import tqdm

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--no-sandbox")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko")
options.add_experimental_option("detach", True)

article_data_list = []

driver = webdriver.Chrome(options=options)
driver.get("https://news.naver.com/section/105")

# 카테고리 선택
# cat : 1~7
# '과학/일반'을 제외한 7개의 카테고리 수집
stop_len = 10
def crl_cat(cat, stop_len):
  print("-------------------------------- \n")
  print(f"{cat}번 카테고리를 수집합니다.")
  print("-------------------------------- \n")
  # 카테고리 선택
  try:
    element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, f"#ct_wrap > div.ct_scroll_wrapper > div.column0 > div > ul > li:nth-child({cat}) > a"))
      )
    driver.execute_script("arguments[0].click();", element)
    time.sleep(2)
  except TimeoutException:
    print(f"TimeoutException: 카테고리 {cat}을 선택하지 못했습니다.")
    return 'NEXT'

  n1 = 1
  while True:
    print(n1)
    # if len(article_data_list) == stop_len:
      # print('수집중단')
      # break

    for n2 in range(1, 7):  # n2는 1~6까지 반복
      print(n1, '-', n2)
      article_data = crl_article(n1, n2, stop_len)
      if article_data == 'STOP':
        driver.back()
        time.sleep(2)
        print("수집 중지 조건 충족. 다음 카테고리.")
        return 'NEXT'  # 다음 카테고리로 이동
      elif article_data is None:
        print("None 반환")
        time.sleep(2)
        continue
      else:
        article_data_list.append(article_data)  # 유효한 데이터만 추가
        driver.back()
        time.sleep(2)
        if len(article_data_list) == stop_len:
          stop_len += 10

    if n1 % 6 == 0:
      try:
        element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, "#newsct > div.section_latest > div > div.section_more > a")))
        driver.execute_script("arguments[0].click();", element)
        time.sleep(2)
        print("더보기 버튼을 클릭했습니다.")
      except TimeoutException:
        print("더보기 버튼을 찾을 수 없습니다. 수집을 종료합니다.")
        break  # 더보기 버튼이 없을 경우 수집 종료
    
    print('다음 n1')
    # n1 값을 1씩 증가시켜 다음 그룹으로 설정
    n1 += 1

  return article_data_list
  
# 기사 수집
# 제목, 작성일자, 언론사, 요약, 기사링크, 기사 이미지 주소
# 1-1 ~ 1-6 존재, 1~ 6 존재 총 36개씩
# 사진은 없는 것도 있음
def crl_article(n1, n2, stop_len):
  element = WebDriverWait(driver, 10).until(
      #newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META > div:nth-child(12) > ul > li:nth-child(6) > div > div > div.sa_text > a > strong
    EC.presence_of_element_located((By.CSS_SELECTOR, f"#newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META > div:nth-child({n1}) > ul > li:nth-child({n2}) > div > div > div.sa_text > a > strong"))
    )
  title = driver.execute_script("return arguments[0].innerText;", element)
  print(title)
  for article in article_data_list:
      if article['title'] == title:
          # print(f"중복된 제목 발견: {title}")
          return None

  element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, f"#newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META > div:nth-child({n1}) > ul > li:nth-child({n2}) > div > div > div.sa_text > div.sa_text_info > div.sa_text_info_left > div.sa_text_press"))
    )
  company = driver.execute_script("return arguments[0].innerText;", element)
  # 세부 페이지로 이동
  element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, f"#newsct > div.section_latest > div > div.section_latest_article._CONTENT_LIST._PERSIST_META > div:nth-child({n1}) > ul > li:nth-child({n2}) > div > div > div.sa_text > a > strong"))
    )
  driver.execute_script("arguments[0].click();", element)
  time.sleep(2)

  try:
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, "#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span"))
      )
    date_str = driver.execute_script("return arguments[0].innerText;", element)
  except TimeoutException:
    try:
      element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#content > div.NewsEnd_container__HcfWh > div > div.NewsEnd_main_group__d5k8S > div > div.NewsEndMain_comp_article_head__Uqd6M > div.article_head_info > div.NewsEndMain_article_head_date_info__jGlzH > div > em")))
      date_str = driver.execute_script("return arguments[0].innerText;", element)
    except TimeoutException:
      print("날짜를 찾을 수 없습니다. 다음 기사로 넘어갑니다.")
      driver.back()
      return None
  period = "AM" if "오전" in date_str else "PM"
  date_str_cleaned = date_str.replace("오전", "").replace("오후", "").strip()
  date = datetime.strptime(date_str_cleaned, '%Y.%m.%d. %I:%M')
  sl = stop_len//10
  if sl > 9 : 
    sm = 1
  else : 
    sm = 0
  if period == "PM" and date.hour != 12:
    date = date.replace(hour=date.hour + 12)
  if date.date() >= datetime(2024, 11-sm, 10-sl+sm*31).date():
    driver.back()
    print("none")
    return None  # 11월 8일보다 이후 날짜는 건너뜀
  elif sl == 31:
  # elif date.date() == datetime(2024, 11, 6).date():
    return 'STOP'  # 11월 6일 날짜는 전체 종료
  print('날짜 ok')
  try:
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, f"#dic_area"))
      )
    content = driver.execute_script("return arguments[0].innerText;", element)
  except:
    try:
      element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#comp_news_article > div._article_content")))
      content = driver.execute_script("return arguments[0].innerText;", element)
      print(content)
    except:
      content = "None"
  
  try:
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, f"#img1")))
    img = element.get_attribute("src")
  except:
    try:
      # 모든 하위 요소 중 img 태그를 탐색
      element = WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR, "#comp_news_article > div._article_content > div > span > span > span > img"))
          )
      img = element.get_attribute("src")
    except:
      try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#comp_news_article > div._article_content > div:nth-child(1) > span > span > span > img")))
        img = element.get_attribute("src")
      except TimeoutException:
        # img 요소를 찾지 못한 경우 기본값 설정
        img = "None"

  try:
    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, f"#ct > div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > a"))
      ) 
    link = element.get_attribute("href")
  except:
    element = WebDriverWait(driver=driver, timeout=10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, f"#content > div.NewsEnd_container__HcfWh > div > div.NewsEnd_main_group__d5k8S > div > div.NewsEndMain_comp_article_head__Uqd6M > div.article_head_info > div.NewsEndMain_article_head_date_info__jGlzH > a")))
    link = element.get_attribute("href")

  # 수집된 기사 데이터를 딕셔너리 형태로 저장
  article_data = {
      "title": title,
      "date": date,
      "company": company,
      "content": content,
      "img": img,
      "link": link
  }
  return article_data

for cat in range(1, 8):
  if crl_cat(cat, stop_len) == 'NEXT':
    continue
  else:
    print(f"{cat}번 카테고리 수집 완료")

import csv

with open("articles.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["title", "date", "company", "content", "img", "link"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    
    for article in article_data_list:
        writer.writerow(article)

print("CSV 파일로 저장 완료: articles.csv")
