import boto3
import pymysql
from datetime import datetime
import pytz
import os
import mimetypes
import cv2
import numpy as np


# 웹캠으로 S3 로 저장 mysql 저장 하는방법 

# MySQL 연결 함수
def mysql_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
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
            service_name=os.getenv('AWS_SERVICE_NAME'),
            region_name=os.getenv('AWS_REGION_NAME'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
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

# YOLO 모델을 로드하는 함수
def load_yolo_model(cfg_path, weights_path, names_path):
    net = cv2.dnn.readNet(weights_path, cfg_path)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

    with open(names_path, "r") as f:
        classes = [line.strip() for line in f.readlines()]

    return net, classes, output_layers

# 객체를 감지하고 이미지 저장하는 함수
def detect_and_save_image(net, output_layers, frame, classes):
    height, width, channels = frame.shape

    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    class_ids = []
    confidences = []
    boxes = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    
        

    for i in range(len(boxes)):
        if i in indexes:
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            color = (0, 255, 0)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_name = f"detected_{timestamp}.jpg"
            cv2.imwrite(image_name, frame)
            return image_name

    return None


if __name__ == "__main__":
    
    s3 = s3_connection()
    if s3:
        cap = cv2.VideoCapture(0)

        cfg_path = "./yolov3-tiny.cfg"
        weights_path = "./yolov3-tiny.weights"
        names_path = "./label.names" 

        if not os.path.isfile(cfg_path) or not os.path.isfile(weights_path) or not os.path.isfile(names_path):
            print("Error: YOLO configuration or weight files not found.")
        else:
            net, classes, output_layers = load_yolo_model(cfg_path, weights_path, names_path)

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("캡처 종료")
                    break

                cv2.imshow("Video", frame)
                if cv2.waitKey(60) == ord('q'):
                    print("영상 종료")
                    break

                detected_image = detect_and_save_image(net, output_layers, frame, classes)
                if detected_image:
                    s3_url = upload_file_to_s3_and_get_url(s3, detected_image, "factorys", detected_image)
                    if s3_url:
                        connection = mysql_connection()
                        if connection:
                            insert_image_url_to_mysql(connection, detected_image, s3_url)
                            connection.close()
                    os.remove(detected_image)

            cap.release()
            cv2.destroyAllWindows()



# MySQL에서 데이터를 조회하는 함수
# def fetch_images_from_mysql(connection):
#     try:
#         with connection.cursor() as cursor:
#             sql = "SELECT * FROM myapp_images"
#             cursor.execute(sql)
#             results = cursor.fetchall()
#             for row in results:
#                 print(row)
#     except pymysql.MySQLError as e:
#         print(f"Error fetching data from MySQL: {e}")

# if __name__ == "__main__":
#     s3 = s3_connection()
#     if s3:
#         file_name = "./myproject/myapp/img/sss.png"
#         object_name = "아앙.jpg"
#         s3_url = upload_file_to_s3_and_get_url(s3, file_name, "factorys", object_name)
#         if s3_url:
#             connection = mysql_connection()
#             if connection:
#                 insert_image_url_to_mysql(connection, object_name, s3_url)
#                 fetch_images_from_mysql(connection)  # Fetch and print the images
#                 connection.close()
