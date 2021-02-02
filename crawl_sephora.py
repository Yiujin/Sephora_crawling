#!/usr/bin/env python
# coding: utf-8

# In[18]:


import pymysql
import os
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from tqdm import tqdm
import json


# In[19]:


class Connect_db:
    def __init__(self, DBinfo , port = 3306, db_name = 'jangho'):
        DBInfo = DBinfo
        self.sephora_db = pymysql.connect(
        user= DBInfo['USERNAME'], 
        passwd=DBInfo['PASSWORD'], 
        host = DBInfo['HOST'], 
        port = port,
        charset='utf8'
        )
        self.db_name = db_name

    def get_sql(self, table_name:list):
        '''
        table마다 review_count 가 0인 행을 가져와 dataframe으로 만듬
        
        <return>
        모든 table 을  concat한 dataframe
        '''
        self.df =  pd.DataFrame()
        for tbl in table_name:
            sql = f'''
            select series_id, item_no, url, product_code, score, review_count, like_count, is_use
            from {self.db_name}.{tbl}
            where (review_count = 0 and like_count !=0) or (score =0 and like_count !=0) ;
            '''
        
            tmp = pd.read_sql(sql, con = self.sephora_db)
            tmp['table_name'] = tbl
            
            #각테이블 마다 행수 출력
            print(f"{tbl} 의 행 개수: ",len(tmp[tmp['table_name']  == f'{tbl}']))
            
            self.df = pd.concat([self.df,  tmp], axis=0,ignore_index=True)
        
        self.sephora_db.close()
        return self.df
    
    def connect_driver(self):
        self.driver = webdriver.Chrome(ChromeDriverManager().install())
        # driver.fullscreen_window()
        self.driver.implicitly_wait(5) # 5초까지 기다려준다. 5초 안에 웹 화면이 표시되면 바로 다음 작업이 진행됨
    
    def get_content_by_url(self, url) -> list:
        '''
        url 을 받아 driver.get 으로 가져오기
        case1 : 크롤링 잘됨  // 페이지형식 바뀌면 xpath 변경 필요 or xpath 말고 공통된 id로 가져오게 바꾸기
        case2 : 될때도 있고,, 안될때도 있고,,  // 그냥 case1 뜰때까지 돌리기 
        
        <return>
        긁어온 review, score
        '''
        try:
            self.driver.get(url)
        except  Exception as e:
            print(f'[driver.get]: {e}')

        # ------------팝업 창 뜰 때 x 버튼 누르기
        try:
            time.sleep(1)
            xbox = self.driver.find_element_by_xpath(f'/html/body/div[3]/div/div/div[2]/div/div/button')  
            xbox.click()
            time.sleep(0.5)
        except:
            pass


        # ------------ product 있는 지 확인
        try:
            time.sleep(1)
    #         try:
    #             continue_shopping()
    #         except Exception as e:
    #             print("로그인 팝업 안꺼짐", e)
    #             pass
            sorry = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/div/div/div/main/div[1]/div[1]/h1').text
            if len(sorry) > 0: # sorry 가  있으면 상품 없는거니가 -1, -1  반환
                return -1, -1
        except Exception as e:
    #         print(f'product 있음 (sorry x): {e}, {url}')
            pass


        # ------------ratings-reviews 가져오기
            # 스크롤  높이 가져옴
        last_height = self.driver.execute_script("return document.body.scollHeight")
        time.sleep(0.5)
        while True:
            # 스크롤 다운
            self.driver.execute_script("window.scrollTo(0, window.scrollY+750)")

            time.sleep(3)

            try: ###### case1
                time.sleep(1)
                try: # 점수, 리뷰 있을 때
                    review = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div[1]')
                    score = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/div[2]')           

                    if len(review.text) > 1 and len(score.text) > 1:
                        print(review.text.split(' ')[0], score.text.split(' ')[0])
                        return [review.text.split(' ')[0], score.text.split(' ')[0]]

                except Exception as e: #점수, 리뷰 없을 때
                    no_star = self.driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[2]/div[1]/div/div[2]/div').get_attribute("aria-label")
                    if no_star == 'No stars':
                        return 0,0

            except Exception as e: ###### case2
                print(f'case 2 start')

                time.sleep(1)
    #             review = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[12]/div[2]/div[2]/div[1]/div/div[2]/span')
    #             score = driver.find_element_by_xpath('/html/body/div[1]/div[2]/div/main/div/div[12]/div[2]/div[2]/div[1]/div/div[2]/div[1]')
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
                    print("case2 no id\n", e)
                    return 0,0

                # 스크롤 다운 후 스크롤 높이 다시 가져옴
            new_height = self.driver.execute_script("return window.scrollY+750")
            last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        self.driver.quit()


# In[20]:


def assert_df(df):
    is_use_minus = df[df['is_use'] == -1]
    no_page = df[df['score'] == -1]
    not_use_yes_data =df[(df['is_use'] ==  -1) & (df['score'] != -1)]

    if(len(is_use_minus) - len(no_page)) != len(not_use_yes_data):
        print("페이지 확인 필요")
        return False
    else:
        return True


# In[21]:


def getDBInfo(jsonFile, key):
    key = 'base'
    DBInfo = json.loads(open(jsonFile).read())
    return DBInfo[key]


# In[22]:


if __name__  == "__main__":
#     MAKE_LIST = True
    MAKE_LIST = False
    
#     CRAWLING_MODE = True
    CRAWLING_MODE = False
    
    DATE = '210126'
    
    table_name = [f'sephora_eye_data_{DATE}',  f'sephora_face_base_data_{DATE}', f'sephora_lip_color_data_{DATE}', f'sephora_moisturizers_data_{DATE}']

    # get db connect-info
    json_file = 'ujinDB.json'
    mycelebsDBInfo = getDBInfo(json_file, 'base')
    
    #### --------start-------- ####
    cc = Connect_db(mycelebsDBInfo, port = 3306, db_name = 'jangho')
    df = cc.get_sql(table_name)
    display(df)
    
    # 수집해야하는 list excel 로 만들기
    if MAKE_LIST:
        df.to_excel('review_rating_list.xlsx', index = False)
        print("save review_rating_list.xlsx")
        
    cc.connect_driver()
    
    #  크롤링 
    if CRAWLING_MODE:
        for idx in tqdm(range(5)):
            url = df['url'].iloc[idx]
            r, s = cc.get_content_by_url(url)
            print(r,s)

            df['review_count'].iloc[idx] = r
            df['score'].iloc[idx] = s
            
    print("----------------------크롤링 끝")
    
    # 크롤링 잘  됐나 확인
    check = assert_df(df)
    
    if check:
        result = df[['series_id', 'product_code', 'item_no', 'score', 'review_count' , 'table_name']]
        display(result)
        result.to_excel(f"review_rating_result_{DATE}.xlsx", encoding = 'utf-8-sig', index = False)
        print(f"결과물 엑셀로 저장 완료 : review_rating_result_{DATE}.xlsx")


# In[ ]:




