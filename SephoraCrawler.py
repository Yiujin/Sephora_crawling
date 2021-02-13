#!/usr/bin/env python
# coding: utf-8


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import requests as rq
from tqdm import tqdm
import datetime


class SephoraCrawler:
    def  __init__(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # driver.fullscreen_window()
        self.driver.implicitly_wait(5) # 5초까지 기다려준다. 5초 안에 웹 화면이 표시되면 바로 다음 작업이 진행됨
            
    def getContentByURL(self, url):
        '''
        url 을 받아 driver.get 으로 가져오기
        case1 : 크롤링 잘됨  // 페이지형식 바뀌면 xpath 변경 필요 (or xpath 말고 공통된 id로 가져오게 바꾸기)
        case2 : 될때도 있고,, 안될때도 있고,,  // 그냥 case1 뜰때까지 돌리기 
        
        <return>
        긁어온 review, score
        '''
        try:
            self.driver.get(url)
        except  Exception as e:
            print(f'[driver.get]: {e}')

        # ------------ 팝업 창 뜰 때 x 버튼 누르기
        try:
            time.sleep(0.5)
            xbox = self.driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div[2]/div/div/button')  
            xbox.click()
            time.sleep(0.5)
        except:
            pass
        
        # ------------ product 있는 지 확인
        try:
            time.sleep(1)
            sorry = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/main/div[1]/div[1]/h1').text
#             print(sorry)
            if len(sorry) > 0: # sorry 가  있으면 상품 없는거니가 -1, -1  반환
                return -1, -1
        except Exception as e: #product 있으면 내린 후 내용 가져오기  
#            print(e)
            pass
        
        while True:
            print(f'case 2 start')
            self.driver.execute_script("window.scrollTo(0, window.scrollY+1500)")
            time.sleep(1)                           
            try: #점수, 리뷰 있을때 
                review_rating_elem = self.driver.find_elements_by_id("ratings-reviews-container")
                elem=[]
                for  value in review_rating_elem:
                    elem = value.text.split('\n')   
                print(elem)

                score = elem[8]
                review = elem[9].split(' ')[0]
#                 print(score, review)
                return review, score

            except Exception as e: # 점수, 리뷰 없을 때
                print("case2 no id:", e)
                if (len(elem) < 2) : print(f"url: {url}")
                return 0,0        
      
    
        while True:
            print(f'case 1 start')
            self.driver.execute_script("window.scrollTo(0, window.scrollY+750)")
            time.sleep(1)
            try: # 점수, 리뷰 있을 때
                review = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div[1]')
                score = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/div[2]')           

                if len(review.text) > 1 and len(score.text) > 1:
                    print(review.text.split(' ')[0], score.text.split(' ')[0])
                    return [review.text.split(' ')[0], score.text.split(' ')[0]]

            except Exception as e: #점수, 리뷰 없을 때
                try:
                    no_star = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div').get_attribute("aria-label")
                    if no_star == 'No stars':
                        return 0,0
                except:
                    break
                
            
    def __exit__(self):
        self.driver.quit()


# In[126]:


# tt = SephoraCrawler()
# for ur in li:
#     r  ,s = tt.getContentByURL(ur)
#     print(r,s)

