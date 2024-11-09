import subprocess
import pymysql

all_keywords = []

# 개별 데이터 처리 확인
def ollama_query(prompt):
    result = subprocess.run(
        ['ollama', 'run', 'llama3.2:latest'],
        input=prompt,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    if result.returncode != 0:
        print("Error:", result.stderr)  # 에러 메시지 출력
    return result.stdout.strip()

db_config = {
    'host': 'readit-mysql.ct026sge4qfq.ap-northeast-2.rds.amazonaws.com',
    'user': 'team4',
    'password': 'readit2024',
    'database': 'readit',
    'charset': 'utf8mb4'
}
try:
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용하여 결과를 딕셔너리 형태로 반환
    print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
    
    select_query = "SELECT * FROM article"
    cursor.execute(select_query)
    
    articles = cursor.fetchall()
    for article in articles:
        content = article['original']
        if content != None:
            summary_prompt = f"다음 기사를 요약하세요:\n\n{content}"
            summary_response = ollama_query(summary_prompt)

            keywords_prompt = f"위 요약에서 핵심 키워드 하나를 추출해주고 대답을 키워드만 해줘:\n\n{summary_response}"
            keyword_response = ollama_query(keywords_prompt)
            all_keywords.append(keyword_response)
            print(keyword_response)
except Exception as e:
    print(f"MySQL 연결 또는 조회 중 오류 발생: {e}")

finally:
    # 연결 종료
    if connection:
        connection.close()
        print("MySQL 연결이 종료되었습니다.")


# 디비에서 가져와서 한번에 처리 및 요약 업데이트
def process_articles():
    all_keywords = []
    try:
        connection = pymysql.connect(**db_config)
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
        
        # 모든 기사 가져오기
        select_query = "SELECT * FROM article"
        cursor.execute(select_query)
        articles = cursor.fetchall()

        for article in articles:
            article_id = article['id']
            content = article['original']
            
            # 기사 내용 요약
            summary_prompt = f"다음 기사를 요약하세요:\n\n{content}"
            summary_response = ollama_query(summary_prompt)
            
            if summary_response:
                #print(f"기사 ID {article_id}의 요약:", summary_response)
                
                # 요약을 DB에 업데이트하고 original 필드를 NULL로 설정
                update_query = "UPDATE article SET summary = %s, original = NULL, updated_at = %s WHERE id = %s"
                cursor.execute(update_query, (summary_response, datetime.now(), article_id))
                connection.commit()

                # 요약에서 핵심 키워드 하나 추출
                keywords_prompt = f"위 요약에서 핵심 키워드 하나를 추출해주고 대답을 키워드만 해줘:\n\n{summary_response}"
                keyword_response = ollama_query(keywords_prompt)
                
                if keyword_response:
                    print(f"기사 ID {article_id}의 핵심 키워드:", keyword_response)
                    all_keywords.append(keyword_response)
                else:
                    print(f"기사 ID {article_id}의 키워드 추출 실패")
            else:
                print(f"기사 ID {article_id}의 요약 생성 실패")
                
    except Exception as e:
        print(f"MySQL 연결 또는 처리 중 오류 발생: {e}")
    finally:
        # 연결 종료
        if connection:
            connection.close()
            print("MySQL 연결이 종료되었습니다.")
    
    return all_keywords

if __name__ == "__main__":
    keywords = process_articles()
    print("모든 키워드 리스트:", keywords)
