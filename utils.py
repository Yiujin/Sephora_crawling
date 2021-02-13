#!/usr/bin/env python
# coding: utf-8

import json
from DBConnection import DBConnection
import pandas as pd


def getDBInfo(jsonFile, key):
    key = 'base'
    DBInfo = json.loads(open(jsonFile).read())
    return DBInfo[key]


def getSQL(DBinfo, table_name:list, port_num = 3306, db_name =  'jangho'):
    DBInfo = DBinfo
    port =  port_num
    db_name = db_name
    db = DBConnection(DBInfo, port, db_name)
    
    with db:
        df = pd.DataFrame()
        
        for tbl in table_name:
            sql = f'''
            select series_id, item_no, url, product_code, score, review_count, like_count, is_use
            from {db_name}.{tbl}
            where (review_count = 0 and like_count !=0) or (score =0 and like_count !=0) ;
            '''
            
            db.cursor.execute(sql)
            tmp = pd.DataFrame(db.cursor.fetchall())
            
#             tmp = pd.read_sql(sql, con = db)
            tmp['table_name'] = tbl
            
            #각테이블 마다 행수 출력
            print(f"{tbl} 의 행 개수: ",len(tmp[tmp['table_name']  == f'{tbl}']))
            
            df = pd.concat([df,  tmp], axis=0,ignore_index=True)
    
    return df


def assert_df(_df):
    df = _df
    is_use_minus = df[df['is_use'] == -1]
    no_page = df[df['score'] == -1]
    not_use_yes_data =df[(df['is_use'] ==  -1) & (df['score'] != -1)]

    if(len(is_use_minus) - len(no_page)) != len(not_use_yes_data):
        print("페이지 확인 필요")
        return False
    else:
        return True

