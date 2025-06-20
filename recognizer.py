import cv2
import numpy as np
import face_recognition

import os
from db import mark_attendance
from datetime import datetime

path = 'Training_images'
images=[]
classNames =[]
myList = os.listdir(path)
print(f"Training on: {myList}")

for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

print("Class Names:",classNames)

def find_encodings(images):
    encodeList =[]
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        try:
            encode=face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        except IndexError:
            print("Warning: No face found in training image")
        return encodeList

encodeListKnown = find_encodings(images)
print("Encoding complete:")

cap = cv2.VideoCapture(0)

while True:
    success,img = cap.read()
    if not success:
        break


    img_small = cv2.resize(img,(0,0),None,0.25,0.25)
    img_rgb = cv2.cvtColor(img_small,cv2.COLOR_BGR2RGB)

    faces_cur_frame = face_recognition.face_locations(img_rgb)
    encodes_cur_frame = face_recognition.face_encodings(img_rgb,faces_cur_frame)

    for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
        matches = face_recognition.compare_faces(encodeListKnown, encode_face)
        face_dis = face_recognition.face_distance(encodeListKnown, encode_face)

        match_index = np.argmin(face_dis)

        if matches[match_index]:
            name = classNames[match_index]
            roll_no = name  # Assuming roll_no is stored as image filename

            # Mark attendance via DB
            mark_attendance(roll_no)

            # Draw bounding box
            y1, x2, y2, x1 = face_loc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name.upper(), (x1 + 6, y2 - 6),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Attendance System', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()