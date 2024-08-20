from flask import Flask, Response, render_template
import cv2
import numpy as np
import logging
import boto3
import pymysql
from datetime import datetime
import pytz
import os
import mimetypes
import roslibpy
from dotenv import load_dotenv
from keras.models import load_model

import threading
import time
# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)


#모델불러오기
model = load_model(r"./model-s3-stream/ai_models/komodel.h5", compile=False)
class_names = open(r"./model-s3-stream/ai_models/kolabels.txt", "r").readlines()

app = Flask(__name__) 

classes = []

# ROS 설정 및 메인 루프
ros_host = "192.168.0.11"
ros_port = 9090

ros = roslibpy.Ros(host=ros_host, port=ros_port)
ros.run()

# QR코드 추적 및 상태 캡처
last_location = None
capture_requested = False
car_id_list = []
location_list = []

save_folder = 'img'


cap = cv2.VideoCapture(0)

# 검출하고 싶은 장소
location_target = "3-3"

# 폴더가 있는지 확인하고 없는 경우 생성합니다.
if not os.path.exists(save_folder):
    os.makedirs(save_folder)
    logging.info(f"Created directory: {save_folder}")

# ROS 로부터 QR 토픽이 날아오면 그걸 전달받아서 동작할 함수
def on_message_received(message):
    global capture_requested
    global car_id_list
    global location_list

    car_id, location = message['data'].split(',')

    if location :
        logging.info(f"topic : {car_id}번 자동차는 {location}에 있습니다!")
    
    try :
        if len(car_id_list) == 0 :
            car_id_list.append(car_id)
            location_list.append(location)
            capture_requested = True if location == location_target else False
        else :
            if car_id_list[-1] != car_id or location_list[-1] != location :
                car_id_list.append(car_id)
                location_list.append(location)
                capture_requested = True if location == location_target else False

    except :
        pass

    if len(car_id_list) == 100 :
        car_id_list.clear()
        location_list.clear()

qr_topic = roslibpy.Topic(ros, 'qr', 'std_msgs/String')
qr_topic.subscribe(on_message_received)

# S3 연결 기능
def s3_connection():
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=os.getenv('AWS_REGION_NAME', 'us-west-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        logging.info("S3 bucket connected!")
        return s3
    except Exception as e:
        logging.error(f"Error connecting to S3: {e}")
        return None

s3 = s3_connection()

# S3에 파일 업로드 및 URL 가져오기
def upload_file_to_s3_and_get_url(s3, file_path, bucket_name, object_name):
    try:
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'binary/octet-stream'

        with open(file_path, 'rb') as file:
            s3.upload_fileobj(
                file,
                bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )
        logging.info("File uploaded successfully")
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        return None

# MySQL 연결 기능
def mysql_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'ls-2fba5d616ed19fb5499c5ae6c43bf72bc772ca47.c9um400asul8.ap-northeast-2.rds.amazonaws.com'),
            user=os.getenv('MYSQL_USER', 'admin'),
            password=os.getenv('MYSQL_PASSWORD', '12345678'),
            database=os.getenv('MYSQL_DATABASE', 'images_db'),
        )
        logging.info("MySQL connection successful")
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to MySQL: {e}")
        return None

connection = mysql_connection()

# 현재 한국 시간 가져오기
def get_kst_time():
    kst = pytz.timezone('Asia/Seoul')
    kst_time = datetime.now(kst)
    return kst_time.strftime('%Y-%m-%d %H:%M:%S')

# MySQL에 이미지 URL 삽입
def insert_image_url_to_mysql(connection, classification="def_front", category="폐주물 창고", image_name=None, image_url=None) :
    try:
        with connection.cursor() as cursor:
            detection_time = get_kst_time()
            sql = "INSERT INTO myapp_images (classification, category, detection_time, image_name, image_url) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (classification, category, detection_time, image_name, image_url))
        connection.commit()
        logging.info("Image URL inserted successfully")
    except pymysql.MySQLError as e:
        logging.error(f"Error inserting URL to MySQL: {e}")

# S3 연결 기능
def s3_connection():
    try:
        s3 = boto3.client(
            service_name='s3',
            region_name=os.getenv('AWS_REGION_NAME', 'us-west-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )
        logging.info("S3 bucket connected!")
        return s3
    except Exception as e:
        logging.error(f"Error connecting to S3: {e}")
        return None

# S3에 파일 업로드 및 URL 가져오기
def upload_file_to_s3_and_get_url(s3, file_path, bucket_name, object_name):
    try:
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'binary/octet-stream'

        with open(file_path, 'rb') as file:
            s3.upload_fileobj(
                file,
                bucket_name,
                object_name,
                ExtraArgs={'ContentType': content_type}
            )
        logging.info("File uploaded successfully")
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{object_name}"
        return s3_url
    except Exception as e:
        logging.error(f"Error uploading file to S3: {e}")
        return None
    
# 영상 쏴주는 함수
def generate():

    global capture_requested
    upload_cnt = 0
    # cap = cv2.VideoCapture(0) 
    # aa = cv2.imread('./model-s3-stream/mom6.jpeg')
    if not cap.isOpened():
        logging.error("Error: Could not open video capture device.")
        return
    try : 
        while True:
            ret, img = cap.read()
            # 그레이스케일 변환
            if not ret:
                logging.error("Error: Could not read frame from video capture device.")
                break

            else :
                if capture_requested :

                    upload_cnt += 1
                    print(f"{location_target} 장소에서의 {upload_cnt}번째 검출 순간")
                    img_name = f"capture_{datetime.now()}.jpg"
                    cv2.imwrite(save_folder + "/" + img_name, img)


                    # img1 =  cv2.imread(save_folder + "/" + img_name)
                   
                    gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

       
                    # 케니 엣지 검출
                    median_intensity = np.median(gray1)
                    lower_threshold = int(max(0, (0.8 - 0.12) * median_intensity))
                    upper_threshold = int(min(255, (1.0 + 0.25) * median_intensity))
                    image_canny = cv2.Canny(gray1, lower_threshold, upper_threshold)
                    
                    # 가우시안 블러 적용
                    img_blurred = cv2.GaussianBlur(image_canny, ksize=(5, 5), sigmaX=0)
                    
                    # 적응형 이진화 적용
                    img_blur_thresh = cv2.adaptiveThreshold(
                        img_blurred,
                        maxValue=255.0,
                        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        thresholdType=cv2.THRESH_BINARY_INV,
                        blockSize=15,
                        C=10
                    )
                    


                    img2 = cv2.cvtColor(img_blur_thresh, cv2.COLOR_GRAY2RGB)


                    # 3번 진행하면 될 듯 
                    frame = cv2.resize(img2, (200, 200))
                
                    frame = frame / 255.0
               
                    frame = np.expand_dims(frame, axis=0)
                  
                    prediction = model.predict(frame)
                    

                    index = np.argmax(prediction)
                    class_name = class_names[index]
                    confidence_score = prediction[0][index]

                    # Print prediction and confidence score
                    print("Class:", class_name, end="")
                    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

                    if "def" in class_name :
                        t = datetime.now().strftime(f'%Y-%m-%dT%H:%M:%S')
                        insert_image_url_to_mysql(connection, image_name=img_name,  image_url=f"https://factorys.s3.amazonaws.com/capture_{t}.jpg")
                        upload_file_to_s3_and_get_url(s3, file_path=f"img/{img_name}", bucket_name="factorys", object_name=f"capture_{t}.jpg")
                    else :
                        insert_image_url_to_mysql(connection, classification="ok_front", category="출하 창고")
                    
                    capture_requested = False

                _, buffer = cv2.imencode('.jpg', img) 
                frame = buffer.tobytes()

                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' 
                        + frame + b'\r\n')

    except KeyboardInterrupt:
        logging.info("Interrupted")
            

def generate_hide():

    global capture_requested
    # aa = cv2.imread('./model-s3-stream/mom6.jpeg')

    upload_cnt = 0

    if not cap.isOpened():
        logging.error("Error: Could not open video capture device.")
        return
    try : 
        while True:
            ret, img = cap.read()
            # 그레이스케일 변환
            if not ret:
                logging.error("Error: Could not read frame from video capture device.")
                break

            else :

                if capture_requested :

                    upload_cnt += 1
                    print(f"{location_target} 장소에서의 {upload_cnt}번째 검출 순간")
                    img_name = f"capture_{datetime.now()}.jpg"
                    cv2.imwrite(save_folder + "/" + img_name, img)


                    img1 =  cv2.imread(save_folder + "/" + img_name)
                    print(img1.shape)
                    gray1 = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

                    print(gray1.shape)
                    # 케니 엣지 검출
                    median_intensity = np.median(gray1)
                    lower_threshold = int(max(0, (0.8 - 0.12) * median_intensity))
                    upper_threshold = int(min(255, (1.0 + 0.25) * median_intensity))
                    image_canny = cv2.Canny(gray1, lower_threshold, upper_threshold)
                    
                    # 가우시안 블러 적용
                    img_blurred = cv2.GaussianBlur(image_canny, ksize=(5, 5), sigmaX=0)
                    
                    # 적응형 이진화 적용
                    img_blur_thresh = cv2.adaptiveThreshold(
                        img_blurred,
                        maxValue=255.0,
                        adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                        thresholdType=cv2.THRESH_BINARY_INV,
                        blockSize=15,
                        C=10
                    )
                    print(img_blur_thresh.shape)


                    img2 = cv2.cvtColor(img_blur_thresh, cv2.COLOR_GRAY2RGB)


                    # 3번 진행하면 될 듯 
                    frame = cv2.resize(img2, (200, 200))
                    print(frame.shape)
                    frame = frame / 255.0
                    print(frame.shape)
                    frame = np.expand_dims(frame, axis=0)
                    print(frame.shape)
                    prediction = model.predict(frame)
                    

                    index = np.argmax(prediction)
                    class_name = class_names[index]
                    confidence_score = prediction[0][index]

                    # Print prediction and confidence score
                    print("Class:", class_name, end="")
                    print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")

                    if "def" in class_name :
                        t = datetime.now().strftime(f'%Y-%m-%dT%H:%M:%S')
                        insert_image_url_to_mysql(connection, image_name=img_name,  image_url=f"https://factorys.s3.amazonaws.com/capture_{t}.jpg")
                        upload_file_to_s3_and_get_url(s3, file_path=f"img/{img_name}", bucket_name="factorys", object_name=f"capture_{t}.jpg")
                    else :
                        insert_image_url_to_mysql(connection, classification="ok_front", category="출하 창고")
                    
                    capture_requested = False


    except KeyboardInterrupt:
        logging.info("Interrupted")
            

@app.route("/video_feed")
def video_feed() :
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    # threading.Thread(target=generate_hide).start()
    app.run(host="0.0.0.0", port="8001", debug=True)


    ros.terminate()
    cap.release()
    cv2.destroyAllWindows()
    logging.info("Terminated ROS client connection.")
