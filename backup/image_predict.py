import face_recognition_api
import cv2
import os
import pickle
import time
import numpy as np
import datetime
import cx_Oracle
import pandas as pd
import csv

connstr = "student/student"
conn = cx_Oracle.connect(connstr)
curs = conn.cursor()
result = curs.execute("select * from test")
result = curs.fetchall()

name_result = [] #db에 있는 학생의 이름 가져오기위해
check_time = [] #들어온 시간 출력
check_name = [] #출석이 된 학생의 이름 받아오기위해
not_in_name = []
not_in_time=[]

for i in range(len(result)):
    name_result.append(result[i][0])

now = datetime.datetime.now()
#print(now)

start = time.clock()
start2 = time.time()
#print(start)
#print(start2)
#뭔가 하는 코드

fname = 'classifier.pkl'
if os.path.isfile(fname):
    with open(fname, 'rb') as f:
        (le, clf) = pickle.load(f)
else:
    print('\x1b[0;37;43m' + "Classifier '{}' does not exist".format(fname) + '\x1b[0m')
    quit()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True



# Grab a single frame of video

small_frame = cv2.imread("44.jpg")

# Resize frame of video to 1/4 size for faster face recognition processing
#small_frame = cv2.resize(frame, (0, 0), fx=2.0,  fy=2.0)

# Only process every other frame of video to save time
if process_this_frame:
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition_api.face_locations(small_frame)
    face_encodings = face_recognition_api.face_encodings(small_frame, face_locations)

    face_names = []
    predictions = []
    if len(face_encodings) > 0:
        closest_distances = clf.kneighbors(face_encodings, n_neighbors=1)

        is_recognized = [closest_distances[0][i][0] <= 0.5 for i in range(len(face_locations))]

        # predict classes and cull classifications that are not with high confidence
        predictions = [(le.inverse_transform(int(pred)).title(), loc) if rec else ("Unknown", loc) for pred, loc, rec in
                       zip(clf.predict(face_encodings), face_locations, is_recognized)]

    # # Predict the unknown faces in the video frame
    # for face_encoding in face_encodings:
    #     face_encoding = face_encoding.reshape(1, -1)
    #
    #     # predictions = clf.predict(face_encoding).ravel()
    #     # person = le.inverse_transform(int(predictions[0]))
    #
    #     predictions = clf.predict_proba(face_encoding).ravel()
    #     maxI = np.argmax(predictions)
    #     person = le.inverse_transform(maxI)
    #     confidence = predictions[maxI]
    #     print(person, confidence)
    #     if confidence < 0.7:
    #         person = 'Unknown'
    #
    #     face_names.append(person.title())

process_this_frame = not process_this_frame


# Display the results
for name, (top, right, bottom, left) in predictions:
    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    top *= 1
    right *= 1
    bottom *= 1
    left *= 1

    # Draw a box around the face
    cv2.rectangle(small_frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Draw a label with a name below the face
    cv2.rectangle(small_frame, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    check_time.append(datetime.datetime.now())
    check_name.append(name)
    cv2.putText(small_frame ,"People: ",(20,200), font,1.0,(255,255,255),1)



for i in range(len(predictions)):
    cv2.putText(small_frame , predictions[i][0],( (i*120)+ 160 ,200), font,1.0,(255,255,255),1)

        #print(check_time[i])

now2 = datetime.datetime.now()

cv2.putText(small_frame , "Start:" + str(now),(20,50), font,1.0,(255,255,255),1)
cv2.putText(small_frame , "End:" + str(now2),(20,100), font,1.0,(255,255,255),1)
cv2.putText(small_frame , "Processing:  " + str(now2-now),(20,150), font,1.0,(255,255,255),1)
# Display the resulting image
cv2.imshow('Video', small_frame)
if not os.path.isdir("./folder"):
    os.mkdir("./folder")
os.chdir("./folder")
cv2.imwrite('5_%d_result .jpg' %1,small_frame)

tm = datetime.datetime.now()
dir_time= tm.strftime('%Y-%m-%d')

path = "./"+dir_time
if os.path.isdir(path):
    print("파일 있당")
    os.chdir(path)
    read_data = pd.read_csv('check.csv') #기존 csv파일 오픈
    for i in range(len(check_name)):
        list_csv=[]
        for j in range(len(read_data['Name'])):
            list_csv.append(read_data['Name'][j])
        if not (check_name[i] in list_csv):
            not_in_name.append(check_name[i])
            not_in_time.append(check_time[i])
    data = {'Name': not_in_name, 'Time': not_in_time}
    dataframe = pd.DataFrame(data)
    dataframe.to_csv("check.csv", mode='a',header=False, index=False)

else:
    print("파일 없음")
    os.mkdir(path)
    os.chdir(path)
    f = open('check.csv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f, delimiter='\t')
    data = {'Name': check_name, 'Time': check_time}
    dataframe = pd.DataFrame(data)
    dataframe.to_csv("check.csv", header=True, index=False)
    f.close()


# Hit 'q' on the keyboard to quit!
#if cv2.waitKey(1) & 0xFF == ord('q'):
 #   break

# Release handle to the webcam
#video_capture.release()
cv2.waitKey(0)
cv2.destroyAllWindows()