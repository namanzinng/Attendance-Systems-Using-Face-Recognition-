import cv2
import csv
import os
import numpy as np
from PIL import Image
import pandas as pd
import datetime
import time
import pymysql.connections

def connect_db(db_name):
    """Connect to a MySQL database and return (connection, cursor)."""
    try:
        conn = pymysql.connect(host='localhost', user='root', password='', database=db_name)
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        print("Database connection error:", e)
        return None, None

def create_attendance_table(cursor, subject, ts):
    """Create an attendance table using the subject and timestamp information."""
    Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour, Minute, Second = timeStamp.split(":")
    table_name = f"{subject}_{Date}_Time_{Hour}_{Minute}_{Second}"
    sql = f"""
    CREATE TABLE {table_name} (
        ID INT NOT NULL AUTO_INCREMENT,
        ENROLLMENT VARCHAR(100) NOT NULL,
        NAME VARCHAR(50) NOT NULL,
        DATE VARCHAR(20) NOT NULL,
        TIME VARCHAR(20) NOT NULL,
        PRIMARY KEY (ID)
    );
    """
    try:
        cursor.execute(sql)
        return table_name
    except Exception as ex:
        print("Table creation error:", ex)
        return None

def insert_attendance_record(cursor, table_name, enrollment, student, ts):
    """Insert a single record of attendance data into the table."""
    Date = datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    sql = f"""
    INSERT INTO {table_name} (ID, ENROLLMENT, NAME, DATE, TIME) 
    VALUES (0, %s, %s, %s, %s)
    """
    values = (str(enrollment), str(student), Date, timeStamp)
    try:
        cursor.execute(sql, values)
    except Exception as e:
        print("Insert error:", e)

def generate_csv_from_table(cursor, table_name, csv_name):
    """Generate a CSV file from the contents of the database table."""
    cursor.execute(f"SELECT * FROM {table_name};")
    with open(csv_name, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([desc[0] for desc in cursor.description])
        csv_writer.writerows(cursor)

def capture_face_images(enrollment, name, sample_limit=70):
    """Capture images from webcam and save face images."""
    cam = cv2.VideoCapture(0)
    detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    sampleNum = 0
    while True:
        ret, img = cam.read()
        if not ret:
            break
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            sampleNum += 1
            filename = f"TrainingImage/{name}.{enrollment}.{sampleNum}.jpg"
            cv2.imwrite(filename, gray)
            cv2.imshow('Frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        elif sampleNum > sample_limit:
            break

    cam.release()
    cv2.destroyAllWindows()
    
    # Initialize connection to insert the student details into the database
    conn, cursor = connect_db('face_reco_fill')  # Initialize connection here
    if conn:
        ts = time.time()
        Date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        TimeStr = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        row = [enrollment, name, Date, TimeStr]
        
        # Insert student details into the 'StudentDetails' table (You need to create this table in DB)
        insert_attendance_record(cursor, 'StudentDetails', enrollment, name, ts)
        conn.commit()  # Commit changes to the DB
        conn.close()   # Close the connection after use
    
    # Save student details to a CSV file
    with open('StudentDetails/StudentDetails.csv', 'a+', newline="") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)
    
    return f"Images saved for Enrollment: {enrollment} Name: {name}"

def get_images_and_labels(path, detector):
    """Extract images and their IDs for training."""
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".jpg")]
    faceSamples = []
    ids = []
    for imagePath in imagePaths:
        pilImage = Image.open(imagePath).convert('L')
        imageNp = np.array(pilImage, 'uint8')
        try:
            Id = int(os.path.split(imagePath)[-1].split(".")[1])  # ID is embedded in the filename
        except IndexError:
            continue  # Skip files that don't match the expected naming convention
        faces = detector.detectMultiScale(imageNp)
        for (x, y, w, h) in faces:
            faceSamples.append(imageNp[y:y + h, x:x + w])
            ids.append(Id)
    return faceSamples, ids

def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    try:
        faces, ids = get_images_and_labels("TrainingImage", detector)
    except Exception as e:
        print("Error in fetching images for training:", e)
        return "Training failed: Check TrainingImage folder."
    recognizer.train(faces, np.array(ids))
    try:
        recognizer.save("TrainingImageLabel/Trainner.yml")
    except Exception as e:
        print("Error saving trainer:", e)
        return 'Please make "TrainingImageLabel" folder.'
    return "Model Trained"

