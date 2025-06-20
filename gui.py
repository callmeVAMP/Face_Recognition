import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import os
import threading
import face_recognition
import numpy as np
from db import mark_attendance, fetch_attendance, add_student_to_db

# Directory to store training images
TRAINING_DIR = 'Training_images'
if not os.path.exists(TRAINING_DIR):
    os.makedirs(TRAINING_DIR)

class FaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Face Attendance System")
        self.root.geometry("600x400")

        self.running = False  # Flag to stop recognition thread on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Buttons
        ttk.Button(root, text="Start Recognition", command=self.start_recognition).pack(pady=10)
        ttk.Button(root, text="View Attendance Logs", command=self.show_logs).pack(pady=10)
        ttk.Button(root, text="Add New Student", command=self.add_student_form).pack(pady=10)

    def start_recognition(self):
        threading.Thread(target=self._recognize_faces).start()

    def _recognize_faces(self):
        images, classNames = [], []
        for file in os.listdir(TRAINING_DIR):
            if file.lower().endswith(('.jpg', '.png')):
                img = cv2.imread(os.path.join(TRAINING_DIR, file))
                if img is not None:
                    images.append(img)
                    classNames.append(os.path.splitext(file)[0])  # e.g., Varsha_22cs02005

        def find_encodings(images, classNames):
            encodeList = []
            validClassNames = []
            for img, name in zip(images, classNames):
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(img)
                if encodings:
                    encodeList.append(encodings[0])
                    validClassNames.append(name)
                else:
                    print(f"[!] Warning: No face found in training image {name}, skipping.")
            return encodeList, validClassNames

        encodeListKnown, classNames = find_encodings(images, classNames)
        print("Encoding complete")

        cap = cv2.VideoCapture(0)
        marked_today = set()
        self.running = True

        while self.running:
            success, img = cap.read()
            if not success:
                break

            imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            faceCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

            for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)

                if matches[matchIndex]:
                    full_id = classNames[matchIndex]  # e.g., Varsha_22cs02005
                    if '_' in full_id:
                        name_part, roll_no = full_id.rsplit('_', 1)
                    else:
                        print(f"[!] Invalid filename format: {full_id}")
                        continue

                    if roll_no not in marked_today:
                        mark_attendance(roll_no)
                        marked_today.add(roll_no)

                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name_part + " (" + roll_no + ")", (x1 + 6, y2 - 6),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            cv2.imshow('Face Attendance', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def on_closing(self):
        self.running = False  # Stop the recognition loop if running
        cv2.destroyAllWindows()
        self.root.destroy()

    def show_logs(self):
        logs = fetch_attendance()
        log_win = tk.Toplevel(self.root)
        log_win.title("Attendance Logs")
        log_win.geometry("600x300")

        tree = ttk.Treeview(log_win, columns=('roll_no', 'date', 'time'), show='headings')
        tree.heading('roll_no', text='Roll No')
        tree.heading('date', text='Date')
        tree.heading('time', text='Time')
        tree.pack(fill='both', expand=True)

        for row in logs:
            tree.insert('', 'end', values=row)

    def add_student_form(self):
        form_win = tk.Toplevel(self.root)
        form_win.title("Add New Student")
        form_win.geometry("600x250")

        tk.Label(form_win, text="Student Name").pack(pady=5)
        name_var = tk.StringVar()
        name_entry = tk.Entry(form_win, textvariable=name_var)
        name_entry.pack()

        tk.Label(form_win, text="Roll Number").pack(pady=5)
        roll_var = tk.StringVar()
        roll_entry = tk.Entry(form_win, textvariable=roll_var)
        roll_entry.pack()

        def capture_image():
            name = name_var.get().strip()
            roll = roll_var.get().strip()
            if not name or not roll:
                messagebox.showerror("Error", "Please enter both name and roll number.")
                return

            cap = cv2.VideoCapture(0)
            messagebox.showinfo("Instructions", "Press SPACE to capture image, ESC to cancel")

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Capture Student Face", frame)

                key = cv2.waitKey(1)
                if key % 256 == 27:  # ESC
                    break
                elif key % 256 == 32:  # SPACE
                    filename = f"{name}_{roll}.jpg"
                    img_path = os.path.join(TRAINING_DIR, filename)
                    cv2.imwrite(img_path, frame)
                    add_student_to_db(name, roll, img_path)
                    messagebox.showinfo("Saved", f"Image saved and student added to database.")
                    break

            cap.release()
            cv2.destroyAllWindows()

        ttk.Button(form_win, text="Capture Image & Save", command=capture_image).pack(pady=20)


# Start the application
if __name__ == "__main__":
    root = tk.Tk()
    app = FaceApp(root)
    root.mainloop()



# import tkinter as tk
# from tkinter import ttk, messagebox
# import cv2
# import os
# import threading
# import face_recognition
# import numpy as np
# from db import mark_attendance, fetch_attendance, add_student_to_db

# # Path to store training images
# TRAINING_DIR = 'Training_images'
# if not os.path.exists(TRAINING_DIR):
#     os.makedirs(TRAINING_DIR)

# class FaceApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Smart Face Attendance System")
#         self.root.geometry("600x400")

#         # Buttons
#         ttk.Button(root, text="Start Recognition", command=self.start_recognition).pack(pady=10)
#         ttk.Button(root, text="View Attendance Logs", command=self.show_logs).pack(pady=10)
#         ttk.Button(root, text="Add New Student", command=self.add_student_form).pack(pady=10)

#     def start_recognition(self):
#         threading.Thread(target=self._recognize_faces).start()

#     def _recognize_faces(self):
#         images, classNames = [], []
#         for file in os.listdir(TRAINING_DIR):
#             if file.lower().endswith(('.jpg', '.png')):
#                 img = cv2.imread(os.path.join(TRAINING_DIR, file))
#                 if img is not None:
#                     images.append(img)
#                     classNames.append(os.path.splitext(file)[0])  # e.g., Varsha_22cs02005

#         def find_encodings(images, classNames):
#             encodeList = []
#             validClassNames = []

#             for img, name in zip(images, classNames):
#                 img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#                 encodings = face_recognition.face_encodings(img)
#                 if encodings:  # Only if a face was detected
#                     encodeList.append(encodings[0])
#                     validClassNames.append(name)
#                 else:
#                     print(f"[!] Warning: No face found in training image {name}, skipping.")

#             return encodeList, validClassNames

#         encodeListKnown, classNames = find_encodings(images, classNames)
#         print("Encoding complete")

#         if not encodeListKnown:
#             messagebox.showerror("Error", "No valid training images with detectable faces.")
#             return

#         cap = cv2.VideoCapture(0)
#         marked_today = set()

#         while True:
#             success, img = cap.read()
#             if not success:
#                 break

#             imgS = cv2.resize(img, (0, 0), fx=0.25, fy=0.25)
#             imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

#             faceCurFrame = face_recognition.face_locations(imgS)
#             encodesCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

#             for encodeFace, faceLoc in zip(encodesCurFrame, faceCurFrame):
#                 matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
#                 faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
#                 matchIndex = np.argmin(faceDis)

#                 if matches[matchIndex]:
#                     full_id = classNames[matchIndex]  # e.g., Varsha_22cs02005

#                     if '_' in full_id:
#                         name_part, roll_no = full_id.rsplit('_', 1)
#                     else:
#                         print(f"[!] Invalid filename format: {full_id}")
#                         continue

#                     if roll_no not in marked_today:
#                         mark_attendance(roll_no)
#                         marked_today.add(roll_no)

#                     y1, x2, y2, x1 = faceLoc
#                     y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
#                     cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
#                     cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
#                     cv2.putText(img, f"{name_part} ({roll_no})", (x1 + 6, y2 - 6),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

#             cv2.imshow('Face Attendance', img)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break

#         cap.release()
#         cv2.destroyAllWindows()

#     def show_logs(self):
#         logs = fetch_attendance()
#         log_win = tk.Toplevel(self.root)
#         log_win.title("Attendance Logs")
#         log_win.geometry("600x300")

#         tree = ttk.Treeview(log_win, columns=('roll_no', 'date', 'time'), show='headings')
#         tree.heading('roll_no', text='Roll No')
#         tree.heading('date', text='Date')
#         tree.heading('time', text='Time')
#         tree.pack(fill='both', expand=True)

#         for row in logs:
#             tree.insert('', 'end', values=row)

#     def add_student_form(self):
#         form_win = tk.Toplevel(self.root)
#         form_win.title("Add New Student")
#         form_win.geometry("600x250")

#         tk.Label(form_win, text="Student Name").pack(pady=5)
#         name_var = tk.StringVar()
#         name_entry = tk.Entry(form_win, textvariable=name_var)
#         name_entry.pack()

#         tk.Label(form_win, text="Roll Number").pack(pady=5)
#         roll_var = tk.StringVar()
#         roll_entry = tk.Entry(form_win, textvariable=roll_var)
#         roll_entry.pack()

#         def capture_image():
#             name = name_var.get().strip()
#             roll = roll_var.get().strip()
#             if not name or not roll:
#                 messagebox.showerror("Error", "Please enter both name and roll number.")
#                 return

#             cap = cv2.VideoCapture(0)
#             messagebox.showinfo("Instructions", "Press SPACE to capture image, ESC to cancel")

#             while True:
#                 ret, frame = cap.read()
#                 if not ret:
#                     break
#                 cv2.imshow("Capture Student Face", frame)

#                 key = cv2.waitKey(1)
#                 if key % 256 == 27:  # ESC
#                     break
#                 elif key % 256 == 32:  # SPACE
#                     filename = f"{name}_{roll}.jpg"
#                     img_path = os.path.join(TRAINING_DIR, filename)
#                     cv2.imwrite(img_path, frame)
#                     add_student_to_db(name, roll, img_path)
#                     messagebox.showinfo("Saved", "Image saved and student added to database.")
#                     break

#             cap.release()
#             cv2.destroyAllWindows()

#         ttk.Button(form_win, text="Capture Image & Save", command=capture_image).pack(pady=20)

# # Run app
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = FaceApp(root)
#     root.mainloop()

