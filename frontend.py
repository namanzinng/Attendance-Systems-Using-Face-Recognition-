import tkinter as tk
from tkinter import Label, Button, Entry, messagebox, ttk
import cv2
import time
import datetime
import csv
import pandas as pd
import os
import subprocess
from PIL import Image, ImageTk

# Import functions from backend
import backend

# Color scheme
PRIMARY_COLOR = "#2c3e50"  # Dark blue
SECONDARY_COLOR = "#3498db"  # Light blue
ACCENT_COLOR = "#e74c3c"  # Red
BACKGROUND_COLOR = "#ecf0f1"  # Light grey
TEXT_COLOR = "#2c3e50"  # Dark blue
WHITE = "#ffffff"

# Fonts
TITLE_FONT = ("Helvetica", 24, "bold")
HEADING_FONT = ("Helvetica", 16, "bold")
BODY_FONT = ("Helvetica", 12)
BUTTON_FONT = ("Helvetica", 12, "bold")


### Helper functions for error dialogs

def err_screen(message_text):
    err_win = tk.Toplevel()
    err_win.geometry('400x150')
    err_win.title('Warning')
    err_win.configure(background=BACKGROUND_COLOR)
    err_win.resizable(False, False)
    
    Label(err_win, text=message_text, fg=ACCENT_COLOR, bg=BACKGROUND_COLOR, 
          font=HEADING_FONT, pady=10).pack()
    
    btn_frame = tk.Frame(err_win, bg=BACKGROUND_COLOR)
    btn_frame.pack(pady=10)
    
    Button(btn_frame, text='OK', command=err_win.destroy, fg=WHITE, bg=SECONDARY_COLOR, 
           width=10, height=1, font=BUTTON_FONT, relief=tk.FLAT).pack()


### Frontend Functions


def manually_fill():
    # Window to enter subject name for manual attendance
    sb = tk.Toplevel()
    sb.title("Manual Attendance")
    sb.geometry('600x300')
    sb.configure(background=BACKGROUND_COLOR)
    sb.resizable(False, False)
    
    main_frame = tk.Frame(sb, bg=BACKGROUND_COLOR)
    main_frame.pack(pady=20)
    
    def fill_attendance():
        ts = time.time()
        subject = SUB_ENTRY.get().strip()
        if subject == '':
            err_screen("Please enter your subject name!")
        else:
            sb.destroy()
            # Connect to DB and create table
            conn, cursor = backend.connect_db('manually_fill_attendance')
            if not cursor:
                err_screen("Database connection error")
                return
            table_name = backend.create_attendance_table(cursor, subject, ts)

            # Build the manual attendance window
            MFW = tk.Toplevel()
            MFW.title(f"Manual Attendance - {subject}")
            MFW.geometry('900x500')
            MFW.configure(background=BACKGROUND_COLOR)
            MFW.resizable(False, False)

            def err_screen_data():
                err_screen("Please enter Student & Enrollment!")

            def enter_data_DB():
                enrollment = ENR_ENTRY.get().strip()
                student = STUDENT_ENTRY.get().strip()
                if enrollment == '' or student == '':
                    err_screen_data()
                else:
                    backend.insert_attendance_record(cursor, table_name, enrollment, student, ts)
                    ENR_ENTRY.delete(0, tk.END)
                    STUDENT_ENTRY.delete(0, tk.END)

            def create_csv():
                # Save CSV and then show its content in a new window
                csv_name = os.path.join(os.getcwd(), table_name + '.csv')
                backend.generate_csv_from_table(cursor, table_name, csv_name)
                csv_win = tk.Toplevel()
                csv_win.title(f"Attendance - {subject}")
                csv_win.configure(background=BACKGROUND_COLOR)
                
                # Create a frame for the table
                table_frame = tk.Frame(csv_win, bg=BACKGROUND_COLOR)
                table_frame.pack(pady=10)
                
                with open(csv_name, newline="") as file:
                    reader = csv.reader(file)
                    for r, row in enumerate(reader):
                        for c, cell in enumerate(row):
                            lbl = tk.Label(table_frame, text=cell, width=18, height=1, fg=TEXT_COLOR,
                                         font=BODY_FONT, bg=WHITE, relief=tk.RIDGE, padx=5, pady=5)
                            lbl.grid(row=r, column=c, sticky="nsew")

                # Add a button to open file explorer
                btn_frame = tk.Frame(csv_win, bg=BACKGROUND_COLOR)
                btn_frame.pack(pady=10)
                
                Button(btn_frame, text="Open Folder", command=lambda: subprocess.Popen(
                       r'explorer /select,"' + os.getcwd() + '"'),
                       fg=WHITE, bg=PRIMARY_COLOR, width=15, font=BUTTON_FONT, relief=tk.FLAT).pack()

            # Main content frame
            content_frame = tk.Frame(MFW, bg=BACKGROUND_COLOR)
            content_frame.pack(pady=20)

            Label(content_frame, text="Enter Enrollment", width=15, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR,
                  font=HEADING_FONT).grid(row=0, column=0, pady=10, padx=10, sticky="e")
            
            ENR_ENTRY = Entry(content_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
            ENR_ENTRY.grid(row=0, column=1, pady=10, padx=10, sticky="w")

            Label(content_frame, text="Enter Student name", width=15, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR,
                  font=HEADING_FONT).grid(row=1, column=0, pady=10, padx=10, sticky="e")
            
            STUDENT_ENTRY = Entry(content_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
            STUDENT_ENTRY.grid(row=1, column=1, pady=10, padx=10, sticky="w")

            # Button frame
            btn_frame = tk.Frame(MFW, bg=BACKGROUND_COLOR)
            btn_frame.pack(pady=20)

            Button(btn_frame, text="Enter Data", command=enter_data_DB, fg=WHITE, bg=SECONDARY_COLOR,
                   width=15, font=BUTTON_FONT, relief=tk.FLAT).grid(row=0, column=0, padx=10)
            
            Button(btn_frame, text="Convert to CSV", command=create_csv, fg=WHITE, bg=SECONDARY_COLOR,
                   width=15, font=BUTTON_FONT, relief=tk.FLAT).grid(row=0, column=1, padx=10)

            MFW.mainloop()

    Label(main_frame, text="Enter Subject:", width=15, height=1,
          fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=HEADING_FONT).grid(row=0, column=0, pady=10, padx=10)
    
    SUB_ENTRY = Entry(main_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
    SUB_ENTRY.grid(row=0, column=1, pady=10, padx=10)
    
    btn_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=20)
    
    Button(btn_frame, text="Continue", command=fill_attendance, fg=WHITE, bg=SECONDARY_COLOR, 
           width=15, font=BUTTON_FONT, relief=tk.FLAT).pack()
    
    sb.mainloop()

def take_img():
    # Get enrollment and name from the main window's entry widgets
    enrollment = txt.get().strip()
    name = txt2.get().strip()
    if enrollment == '' or name == '':
        err_screen("Enrollment & Name required!")
    else:
        result_text = backend.capture_face_images(enrollment, name)
        Notification.configure(text=result_text, bg="SpringGreen3", width=50, font=BODY_FONT)
        Notification.place(x=350, y=400)

def subjectchoose():
    # Frontend for automatic attendance filling
    windo = tk.Toplevel()
    windo.title("Automatic Attendance")
    windo.geometry('600x350')
    windo.configure(background=BACKGROUND_COLOR)
    windo.resizable(False, False)
    
    Notifica = Label(windo, text="", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=40,
                     font=HEADING_FONT, pady=10)

    def fill_attendances():
        subject = tx.get().strip()
        if subject == '':
            err_screen("Please enter your subject name!")
        else:
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            try:
                recognizer.read("TrainingImageLabel/Trainner.yml")
            except Exception as e:
                Notifica.configure(text="Model not found, please train model", bg=ACCENT_COLOR, fg=WHITE, 
                                 width=40, font=HEADING_FONT)
                Notifica.pack(pady=20)
                return

            harcascadePath = "haarcascade_frontalface_default.xml"
            faceCascade = cv2.CascadeClassifier(harcascadePath)
            df = pd.read_csv("StudentDetails/StudentDetails.csv", on_bad_lines='warn')

            cam = cv2.VideoCapture(0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            attendance = pd.DataFrame(columns=['Enrollment', 'Name', 'Date', 'Time'])
            now = time.time()
            future = now + 5  # capture for 20 seconds
            
            # Create a simple processing window
            processing_win = tk.Toplevel()
            processing_win.title("Processing...")
            processing_win.geometry('300x100')
            processing_win.configure(background=BACKGROUND_COLOR)
            Label(processing_win, text="Capturing attendance...", font=HEADING_FONT, 
                  bg=BACKGROUND_COLOR, fg=TEXT_COLOR).pack(pady=20)
            processing_win.update()
            
            while True:
                ret, im = cam.read()
                gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.2, 5)
                for (x, y, w, h) in faces:
                    Id, conf = recognizer.predict(gray[y:y+h, x:x+w])
                    if conf < 70:
                        ts = time.time()
                        date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                        timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                        name_db = df.loc[df['Enrollment'] == Id]['Name'].values
                        label_text = str(Id) + "-" + str(name_db)
                        attendance = attendance.drop_duplicates(['Enrollment'], keep='first')
                        attendance.loc[len(attendance)] = [Id, name_db, date, timeStamp]
                        cv2.rectangle(im, (x, y), (x+w, y+h), (0, 260, 0), 7)
                        cv2.putText(im, label_text, (x+h, y), font, 1, (255, 255, 0), 4)
                    else:
                        cv2.rectangle(im, (x, y), (x+w, y+h), (0, 25, 255), 7)
                        cv2.putText(im, "Unknown", (x+h, y), font, 1, (0, 25, 255), 4)
                if time.time() > future:
                    break
                cv2.imshow('Filling attendance..', im)
                if cv2.waitKey(30) & 0xff == 27:
                    break

            cam.release()
            cv2.destroyAllWindows()
            processing_win.destroy()
            
            ts = time.time()
            date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            Hour, Minute, Second = timeStamp.split(":")
            fileName = "Attendance/" + subject + "_" + date + "_" + Hour + "-" + Minute + "-" + Second + ".csv"
            attendance = attendance.drop_duplicates(['Enrollment'], keep='first')
            attendance.to_csv(fileName, index=False)

            # Database part for attendance
            conn, cursor = backend.connect_db('Face_reco_fill')
            if not cursor:
                err_screen("Database connection error!")
                return
            table_name = f"{subject}_{datetime.datetime.fromtimestamp(ts).strftime('%Y_%m_%d')}_Time_{Hour}_{Minute}_{Second}"
            sql_create = ("CREATE TABLE " + table_name +
                          """ (ID INT NOT NULL AUTO_INCREMENT,
                               ENROLLMENT VARCHAR(100) NOT NULL,
                               NAME VARCHAR(50) NOT NULL,
                               DATE VARCHAR(20) NOT NULL,
                               TIME VARCHAR(20) NOT NULL,
                               PRIMARY KEY (ID));
                          """)
            try:
                cursor.execute(sql_create)
                if not attendance.empty:
                    record = attendance.iloc[0]
                    sql_insert = ("INSERT INTO " + table_name + " (ID, ENROLLMENT, NAME, DATE, TIME) VALUES (0, %s, %s, %s, %s)")
                    cursor.execute(sql_insert, (str(record['Enrollment']), str(record['Name']), date, timeStamp))
            except Exception as ex:
                print(ex)

            Notifica.configure(text='Attendance marked successfully', bg="Green", fg=WHITE,
                             width=40, font=HEADING_FONT)
            Notifica.pack(pady=20)

            # Show CSV content in a new window
            csv_win = tk.Toplevel()
            csv_win.title(f"Attendance - {subject}")
            csv_win.configure(background=BACKGROUND_COLOR)
            
            # Create a frame for the table
            table_frame = tk.Frame(csv_win, bg=BACKGROUND_COLOR)
            table_frame.pack(pady=10)
            
            with open(fileName, newline="") as file:
                reader = csv.reader(file)
                for r, row in enumerate(reader):
                    for c, cell in enumerate(row):
                        lbl = tk.Label(table_frame, text=cell, width=15, height=1, fg=TEXT_COLOR,
                                     font=BODY_FONT, bg=WHITE, relief=tk.RIDGE, padx=5, pady=5)
                        lbl.grid(row=r, column=c, sticky="nsew")

            # Add a button to open file explorer
            btn_frame = tk.Frame(csv_win, bg=BACKGROUND_COLOR)
            btn_frame.pack(pady=10)
            
            Button(btn_frame, text="Open Folder", command=lambda: subprocess.Popen(["open", os.getcwd()]),
                   fg=WHITE, bg=PRIMARY_COLOR, width=15, font=BUTTON_FONT, relief=tk.FLAT).pack()

    main_frame = tk.Frame(windo, bg=BACKGROUND_COLOR)
    main_frame.pack(pady=20)

    Label(main_frame, text="Enter Subject:", width=15, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR, 
          font=HEADING_FONT).grid(row=0, column=0, pady=10, padx=10)
    
    tx = Entry(main_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
    tx.grid(row=0, column=1, pady=10, padx=10)
    
    btn_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    btn_frame.grid(row=1, column=0, columnspan=2, pady=20)
    
    Button(btn_frame, text="Start Attendance", command=fill_attendances, fg=WHITE, bg=SECONDARY_COLOR, 
           width=15, font=BUTTON_FONT, relief=tk.FLAT).pack()

    windo.mainloop()

def admin_panel():
    win = tk.Toplevel()
    win.title("Admin Login")
    win.geometry('500x400')
    win.configure(background=BACKGROUND_COLOR)
    win.resizable(False, False)
    
    Nt = Label(win, text="", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=40,
               font=HEADING_FONT, pady=10)

    def log_in():
        username = un_entr.get().strip()
        password = pw_entr.get().strip()
        if username == 'upes' and password == 'upes':
            win.destroy()
            admin_win = tk.Toplevel()
            admin_win.title("Student Details")
            admin_win.configure(background=BACKGROUND_COLOR)
            
            # Create a frame for the table
            table_frame = tk.Frame(admin_win, bg=BACKGROUND_COLOR)
            table_frame.pack(pady=10)
            
            cs = os.path.join(os.getcwd(), 'StudentDetails/StudentDetails.csv')
            with open(cs, newline="") as file:
                reader = csv.reader(file)
                for r, row in enumerate(reader):
                    for c, cell in enumerate(row):
                        lbl = tk.Label(table_frame, text=cell, width=15, height=1, fg=TEXT_COLOR, 
                                     font=BODY_FONT, bg=WHITE, relief=tk.RIDGE, padx=5, pady=5)
                        lbl.grid(row=r, column=c, sticky="nsew")
        else:
            Nt.configure(text='Incorrect ID or Password', bg=ACCENT_COLOR, fg=WHITE,
                         width=38, font=HEADING_FONT)
            Nt.pack(pady=20)

    main_frame = tk.Frame(win, bg=BACKGROUND_COLOR)
    main_frame.pack(pady=30)

    Label(main_frame, text="Username:", width=10, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR, 
          font=HEADING_FONT).grid(row=0, column=0, pady=10, padx=10, sticky="e")
    
    un_entr = Entry(main_frame, width=20, font=BODY_FONT, relief=tk.FLAT)
    un_entr.grid(row=0, column=1, pady=10, padx=10)

    Label(main_frame, text="Password:", width=10, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR, 
          font=HEADING_FONT).grid(row=1, column=0, pady=10, padx=10, sticky="e")
    
    pw_entr = Entry(main_frame, width=20, show="*", font=BODY_FONT, relief=tk.FLAT)
    pw_entr.grid(row=1, column=1, pady=10, padx=10)

    btn_frame = tk.Frame(main_frame, bg=BACKGROUND_COLOR)
    btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

#
    
    Button(btn_frame, text="Login", command=log_in, fg=WHITE, bg=SECONDARY_COLOR, 
           width=20, font=BUTTON_FONT, relief=tk.FLAT).grid(row=1, column=0, columnspan=2, pady=10)

    win.mainloop()

def trainimg():
    result = backend.train_model()
    Notification.configure(text=result, bg="olive drab", width=50, font=BODY_FONT)
    Notification.place(x=350, y=400)



### Main Window (Frontend)


window = tk.Tk()
window.title("UPES Attendance Portal")
window.geometry('1200x700')
window.configure(background=BACKGROUND_COLOR)

# Header Frame
header_frame = tk.Frame(window, bg=PRIMARY_COLOR)
header_frame.pack(fill=tk.X, pady=(0, 20))

Label(header_frame, text="UPES Attendance Portal", bg=PRIMARY_COLOR, fg=WHITE, 
      font=TITLE_FONT, padx=20, pady=20).pack()

# Main Content Frame
content_frame = tk.Frame(window, bg=BACKGROUND_COLOR)
content_frame.pack(pady=20)

# Student Info Frame
info_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
info_frame.grid(row=0, column=0, padx=20, pady=20)

Label(info_frame, text="Enter SAP ID:", width=15, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR, 
      font=HEADING_FONT).grid(row=0, column=0, pady=10, sticky="e")

txt = Entry(info_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
txt.grid(row=0, column=1, pady=10, padx=10)

#

Label(info_frame, text="Enter Name:", width=15, height=1, fg=TEXT_COLOR, bg=BACKGROUND_COLOR, 
      font=HEADING_FONT).grid(row=1, column=0, pady=10, sticky="e")

txt2 = Entry(info_frame, width=25, font=BODY_FONT, relief=tk.FLAT)
txt2.grid(row=1, column=1, pady=10, padx=10)

#

# Buttons Frame
buttons_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
buttons_frame.grid(row=1, column=0, pady=20)

# First row of buttons
btn_row1 = tk.Frame(buttons_frame, bg=BACKGROUND_COLOR)
btn_row1.pack(pady=10)

Button(btn_row1, text="Take Images", command=take_img, fg=WHITE, bg=SECONDARY_COLOR,
       width=20, font=BUTTON_FONT, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

Button(btn_row1, text="Train Images", command=trainimg, fg=WHITE, bg=SECONDARY_COLOR,
       width=20, font=BUTTON_FONT, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

# Second row of buttons
btn_row2 = tk.Frame(buttons_frame, bg=BACKGROUND_COLOR)
btn_row2.pack(pady=10)

Button(btn_row2, text="Automatic Attendance", command=subjectchoose, fg=WHITE, bg=SECONDARY_COLOR,
       width=20, font=BUTTON_FONT, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

Button(btn_row2, text="Manual Attendance", command=manually_fill, fg=WHITE, bg=SECONDARY_COLOR,
       width=20, font=BUTTON_FONT, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

# Admin button
admin_frame = tk.Frame(content_frame, bg=BACKGROUND_COLOR)
admin_frame.grid(row=2, column=0, pady=20)

Button(admin_frame, text="Admin Panel", command=admin_panel, fg=WHITE, bg=PRIMARY_COLOR,
       width=20, font=BUTTON_FONT, relief=tk.FLAT).pack()

# Notification label
Notification = Label(window, text="", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, width=60,
                     font=BODY_FONT, pady=10)
Notification.pack(pady=20)

def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()

