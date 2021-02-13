#!/usr/bin/env python
# coding: utf-8

import pymysql


class DBConnection:
    """pymysql database connection"""
    def __init__(self, DBinfo ,port =  3306, db_name = 'jangho'):
        DBInfo=DBinfo
        self.host_url = DBInfo['HOST']
        self.user_nm = DBInfo['USERNAME']
        self.passwd = DBInfo['PASSWORD']
        self.port = port
        self.db_name = db_name

    # with구문 진입시에 db와 connection을 하고
    # cursor 를 만든다.
    def __enter__(self):
        self.sephora_db = pymysql.connect(
        user=self.user_nm,
        passwd=self.passwd, 
        host = self.host_url, 
        port = self.port,
        charset='utf8',
        cursorclass = pymysql.cursors.DictCursor
        )
        
        self.cursor = self.sephora_db.cursor()
        
        return self
    
    # with구문을 빠져나오기 전 session을 종료한다.
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        with구문을 빠져나오기 직전에 호출되는 메소드 
        type, value, traceback는 with문을 빠져나오기 전에 예외가 발생했을 때의 정보를 나타냄
        '''
        self.sephora_db.close()
        
    def cursor(self):
        return self.cursor




