import boto3
import pymysql
from io import BytesIO
from datetime import datetime
import pytz
import os
import mimetypes

# MySQL 연결 함수
def mysql_connection():
    try:
        connection = pymysql.connect(
            host='ls-2fba5d616ed19fb5499c5ae6c43bf72bc772ca47.c9um400asul8.ap-northeast-2.rds.amazonaws.com',
            user='admin',
            password='12345678',
            database='images_db',
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# 한국 시간대를 고려하여 현재 시간을 반환하는 함수
def get_kst_time():
    kst = pytz.timezone('Asia/Seoul')
    kst_time = datetime.now(kst)
    return kst_time.strftime('%Y-%m-%d %H:%M:%S')

# 이미지 URL을 MySQL에 삽입하는 함수
def insert_image_url_to_mysql(connection, image_name, image_url):
    try:
        with connection.cursor() as cursor:
            detection_time = get_kst_time()
            sql = "INSERT INTO myapp_images (image_name, image_url, Detection_Time) VALUES (%s, %s, %s)"
            cursor.execute(sql, (image_name, image_url, detection_time))
        connection.commit()
        print("Image URL inserted successfully")
    except pymysql.MySQLError as e:
        print(f"Error inserting URL to MySQL: {e}")

# S3 연결 함수
def s3_connection():
    try:
        s3 = boto3.client(
            service_name="s3",
            region_name='us-east-2',
            aws_access_key_id='AKIA2UC3AWOOPLLJY36R',
            aws_secret_access_key='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',
        )
    except Exception as e:
        print(e)
        return None
    else:
        print("s3 bucket connected!")
        return s3

# 파일을 S3에 업로드하고 URL을 반환하는 함수
def upload_file_to_s3_and_get_url(s3, file_name, bucket_name, object_name):
    try:
        content_type, _ = mimetypes.guess_type(file_name)  # 파일의 MIME 타입 추정
        if content_type is None:
            content_type = 'binary/octet-stream'  # 기본값

        with open(file_name, 'rb') as file:
            s3.upload_fileobj(
                file,
                bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}  # 적절한 Content-Type 설정
            )
        print("File uploaded successfully")
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        print(e)
        return None

# MySQL에서 데이터를 조회하는 함수
def fetch_images_from_mysql(connection):
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM myapp_images"
            cursor.execute(sql)
            results = cursor.fetchall()
            for row in results:
                print(row)
    except pymysql.MySQLError as e:
        print(f"Error fetching data from MySQL: {e}")

if __name__ == "__main__":
    s3 = s3_connection()
    if s3:
        file_name = "./myproject/myapp/img/sss.png"
        object_name = "아앙.jpg"
        s3_url = upload_file_to_s3_and_get_url(s3, file_name, "factorys", object_name)
        if s3_url:
            connection = mysql_connection()
            if connection:
                insert_image_url_to_mysql(connection, object_name, s3_url)
                fetch_images_from_mysql(connection)  # Fetch and print the images
                connection.close()
