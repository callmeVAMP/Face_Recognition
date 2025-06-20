# 🧠 Face Recognition Attendance System

A Python-based smart attendance system that uses real-time face recognition to automate attendance logging, with a GUI interface and MySQL database integration.

---

## 🚀 Features

- 🎥 **Live Face Recognition** using webcam
- 🧠 **Face Encoding** with `face_recognition` library
- 🖼️ Capture and register new student faces
- 🧾 Mark attendance with **timestamp and date**
- 📊 View attendance logs in a GUI table
- 🗃️ MySQL backend for persistent storage
- 🖥️ GUI built using Tkinter
- 🧵 Multithreaded face recognition for a responsive UI

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **OpenCV**
- **face_recognition**
- **NumPy**
- **Tkinter** (GUI)
- **MySQL** (`mysql-connector-python`)

---

## 📸 Screenshots

> (You can add screenshots here if you want, like GUI form or live recognition window)

---

## 📁 Project Structure

```bash
FaceRecognition_AttendanceSystem/
├── gui.py                  # Main GUI application
├── db.py                   # Handles all DB operations
├── Training_images/        # Stores student face images
├── requirements.txt        # Python dependencies
└── README.md
