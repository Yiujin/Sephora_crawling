# Sephora_crawling

### 목표  
Sephora 홈페이지의 리뷰와 점수를 가져옴  
***
  
### 방법   
특정 제품의 url 을 입력하여 페이지가 있으면 해당 제품에 달린 리뷰와 점수를 가져오고
페이지가 없으면 -1, -1 을 반환함   
***
  
### 구성  
utils.py : DB 연결 정보 가져오기, sql 전송하여 테이블 가져오기 등의 함수  
DBConnection.py : pymnysql을 이용하여 Database에 연결 후 cursur 생성 class  
SephoraCrawler.py : selenium을 이용하여 크롤링해오는 class  
CrawlSephoraMain.ipynb : main  
***
  
### 실행  
requirements 모두 설치 후  
CrawlSephoraMain 실행
