import pymysql
from datetime import datetime

db_config = {
    "host": "readit-mysql.ct026sge4qfq.ap-northeast-2.rds.amazonaws.com",
    "port": 3306,
    "user": "team4",
    "password": "readit2024",
    "database": "readit",
    "charset": "utf8mb4",
}
import pymysql
from datetime import datetime

# DB 연결 설정
db_config = {
    'host': 'readit-mysql.ct026sge4qfq.ap-northeast-2.rds.amazonaws.com',
    'user': 'team4',
    'password': 'readit2024',
    'database': 'readit',
    'charset': 'utf8mb4'
}

try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
    
    insert_query = """
    INSERT INTO article (title, pub_date, source, summary, article_link, scrap_count, 
    view_count, img_url, created_at, updated_at, status, original) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), %s, %s)
    """
    
    for _, row in df_merged.iterrows():
        try:
            # date가 문자열인 경우 datetime 객체로 변환
            date_obj = row['date'] if isinstance(row['date'], datetime) else datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S')
            
            # 행 데이터 삽입
            cursor.execute(insert_query, (
                row['title'],
                date_obj,                 # 변환된 날짜를 삽입
                row['company'],
                '',                        # summary 컬럼이 없을 경우 기본값 ''
                row['link'],
                0,                         # scrap_count 초기값
                0,                         # view_count 초기값
                row.get('img', 'None'),    # img 컬럼이 없을 경우 기본값 'None'
                'ACTIVE',                  # 상태 초기값
                row['content']
            ))
            print(f"기사 '{row['title']}'가 성공적으로 추가되었습니다.")
        except Exception as e:
            print(f"'{row['title']}' 추가 중 오류 발생: {e}")

    # 커밋하여 데이터 저장
    connection.commit()

except Exception as e:
    print(f"MySQL 연결 오류: {e}")

finally:
    # 연결 종료
    if connection:
        connection.close()
        print("MySQL 연결이 종료되었습니다.")


# 데이터 조회
# try:
#     connection = pymysql.connect(**db_config)
#     cursor = connection.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용하여 결과를 딕셔너리 형태로 반환
#     print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
    
#     # 데이터 조회 쿼리
#     select_query = "SELECT * FROM article"
#     cursor.execute(select_query)
    
#     # 조회한 데이터 출력
#     articles = cursor.fetchall()
#     for article in articles:
#         print(article)

# except Exception as e:
#     print(f"MySQL 연결 또는 조회 중 오류 발생: {e}")

# finally:
#     # 연결 종료
#     if connection:
#         connection.close()
#         print("MySQL 연결이 종료되었습니다.")
