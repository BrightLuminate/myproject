import logging
import boto3
import pymysql
from datetime import datetime
import pytz
import os
import mimetypes
import cv2
import numpy as np
import roslibpy
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)

# MySQL 연결 기능
def mysql_connection():
    try:
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'mydatabase'),
        )
        logging.info("MySQL connection successful")
        return connection
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to MySQL: {e}")
        return None

# 현재 한국 시간 가져오기
def get_kst_time():
    kst = pytz.timezone('Asia/Seoul')
    kst_time = datetime.now(kst)
    return kst_time.strftime('%Y-%m-%d %H:%M:%S')

# MySQL에 이미지 URL 삽입
def insert_image_url_to_mysql(connection, image_name, image_url):
    try:
        with connection.cursor() as cursor:
            detection_time = get_kst_time()
            sql = "INSERT INTO myapp_images (image_name, image_url, detection_time) VALUES (%s, %s, %s)"
            cursor.execute(sql, (image_name, image_url, detection_time))
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

# YOLO 모델 로딩 기능
def load_yolo_model(cfg_path, weights_path, names_path):
    try:
        net = cv2.dnn.readNet(weights_path, cfg_path)
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

        with open(names_path, "r") as f:
            classes = [line.strip() for line in f.readlines()]

        logging.info("YOLO model loaded successfully")
        return net, classes, output_layers
    except Exception as e:
        logging.error(f"Error loading YOLO model: {e}")
        return None, None, None

# 물체 감지 및 이미지에 레이블 표시
def detect_and_display_objects(net, output_layers, frame, classes):
    try:
        height, width, _ = frame.shape

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
        detected_objects = [classes[class_ids[i]] for i in indexes.flatten()]

        if len(indexes) == 0 or len(detected_objects) == 0:
            logging.info("No relevant objects detected.")
            return frame

        for i in range(len(boxes)):
            if i in indexes.flatten():
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                color = (0, 255, 0)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)

        return frame

    except Exception as e:
        logging.error(f"Error detecting objects: {e}")
        return frame

# ROS 설정 및 메인 루프
ros_host = os.getenv('ROS_HOST', 'localhost')
ros_port = int(os.getenv('ROS_PORT', 9090))

client = roslibpy.Ros(host=ros_host, port=ros_port)
client.run()
subscriber = roslibpy.Topic(client, '/qr', 'std_msgs/String')

# QR코드 추적 및 상태 캡처
last_location = None
capture_requested = False

def location_objecting(message):
    global last_location, capture_requested
    data_ = message['data'].split(',')
    location = data_[1]

    if location != last_location:
        last_location = location
        capture_requested = True
        logging.info(f"Location updated to: {location}")

def capture_and_process_image(frame):
    cfg_path = "./yolov3-tiny.cfg"
    weights_path = "./yolov3-tiny.weights"
    names_path = "./label.names"

    if not os.path.isfile(cfg_path) or not os.path.isfile(weights_path) or not os.path.isfile(names_path):
        logging.error("Error: YOLO configuration or weight files not found.")
        return

    net, classes, output_layers = load_yolo_model(cfg_path, weights_path, names_path)
    if net is None or classes is None or output_layers is None:
        return

    save_folder = 'myproject/myapp/img'
    detected_frame = detect_and_display_objects(net, output_layers, frame, classes)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f"detected_{timestamp}.jpg"
    image_path = os.path.join(save_folder, image_name)

    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    
    cv2.imwrite(image_path, detected_frame)
    logging.info(f"Image saved: {image_path}")

    s3 = s3_connection()
    if s3:
        s3_url = upload_file_to_s3_and_get_url(s3, image_path, "factorys", os.path.basename(image_path))
        if s3_url:
            connection = mysql_connection()
            if connection:
                insert_image_url_to_mysql(connection, os.path.basename(image_path), s3_url)
                connection.close()
    # 필요하지 않으면 로컬 파일 삭제
    # os.remove(image_path)

if __name__ == "__main__":
    subscriber.subscribe(location_objecting)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        logging.error("Error: Could not open video capture device.")
        exit()

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                logging.error("Error: Could not read frame from video capture device.")
                break

            cv2.imshow('Webcam Feed', frame)

            if capture_requested and last_location == "2-1":
                capture_and_process_image(frame)
                capture_requested = False

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        logging.info("Interrupted")

    finally:
        subscriber.unsubscribe()
        client.terminate()
        cap.release()
        cv2.destroyAllWindows()
        logging.info("Terminated ROS client connection.")
