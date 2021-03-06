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

# query를 이용해 db에서 정보 얻어옴
connstr = "test/test"
conn = cx_Oracle.connect(connstr)
curs = conn.cursor()
curs.execute("select name from enroll, student where enroll.stu_id = student.stu_id and enroll.course_id = 'cor_1' ")
result = curs.fetchall()

name_result = [] #db에 있는 학생의 이름 가져오기위해
check_time = [] #들어온 시간 출력
check_name = [] #출석이 된 학생의 이름 받아오기 위해
not_in_name = [] #새로 들어온 사람의 이름을 받기 위해
not_in_time=[] #새로 들어온 사람의 시간을 받기 위해

for i in range(len(result)): #db에서 학생의 이름만 받아옴
     name_result.append(result[i][0])

now = datetime.datetime.now()
#print(now)
fname = 'classifier.pkl'  #학습한 정보 가져옴
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

small_frame = cv2.imread("./test-images/test04/84.jpg")

# Resize frame of video to 1/4 size for faster face recognition processing
small_frame = cv2.resize(small_frame, (1280, 960), cv2.INTER_AREA)

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


process_this_frame = not process_this_frame

# Display the results
for name, (top, right, bottom, left) in predictions:  # 사람 얼굴 인식
    # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    # top *= 1
    # right *= 1
    # bottom *= 1
    # left *= 1

    # Draw a box around the face
    cv2.rectangle(small_frame, (left, top), (right, bottom), (0, 0, 255), 2)

    # Draw a label with a name below the face
    cv2.rectangle(small_frame, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    check_time.append(datetime.datetime.now().strftime('%Y-%m-%d %H-%M'))  # 인식됐을때의 시간 저장
    check_name.append(name)  # 검출된 사람의 이름 저장
    cv2.putText(small_frame, "People: ", (20, 200), font, 1.0, (255, 255, 255), 1)

for i in range(len(predictions)): #전체 사진에서 검출된 사람의 이름 전부 출력
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame , predictions[i][0],( (i*120)+ 160 ,200), font,1.0,(255,255,255),1)
#for i in range(len(predictions)): #전체 사진에서 검출된 사람의 이름 전부 출력
#    check_name.append(predictions[i][0])
#    check_time.append(datetime.datetime.now().strftime('%Y-%m-%d %H-%M'))

now2 = datetime.datetime.now()

font = cv2.FONT_HERSHEY_DUPLEX
cv2.putText(small_frame , "Start:" + str(now),(20,50), font,1.0,(255,255,255),1)
cv2.putText(small_frame , "End:" + str(now2),(20,100), font,1.0,(255,255,255),1)
cv2.putText(small_frame , "Processing:  " + str(now2-now),(20,150), font,1.0,(255,255,255),1)
# Display the resulting image
cv2.imshow('Video', small_frame)

#결과를 폴더를 만들어 저장
if not os.path.isdir("./folder"):
    os.mkdir("./folder")
os.chdir("./folder")
cv2.imwrite('5_%d_result .jpg' %1,small_frame)

tm = datetime.datetime.now()
dir_time= tm.strftime('%Y-%m-%d')
path = "./"+dir_time

#해당날짜에 해당하는 폴더가 있으면 기존 폴더를 열어서 처음 검출된 학생의 이름과 시간만 csv파일에 저장
if os.path.isdir(path):
    print("파일 있당")
    os.chdir(path)
    read_data = pd.read_csv('check.csv') #기존 csv파일 오픈
    for i in range(len(check_name)):
        list_csv=[]
        for j in range(len(read_data['Name'])): #csv파일에서 name만 가져와서 list_csv배열에 저장
            list_csv.append(read_data['Name'][j])
        if not (check_name[i] in list_csv): #검출된 사람의 이름이 csv파일에 없으면 배열에 저장
            not_in_name.append(check_name[i])
            not_in_time.append(check_time[i])
    print("들어온 사람: ", end="")
    print(check_name)
    print("들어온 시간: ", end="")
    print(check_time)
    print("추가로 들어온 사람: ", end="")
    print(not_in_name)
    print("들어온 시간: ", end="")
    print(not_in_time)
    data = {'Name': not_in_name, 'Time': not_in_time}
    dataframe = pd.DataFrame(data)
    dataframe.to_csv("check.csv", mode='a',header=False, index=False)
    if len(not_in_name) >0 :
        input = []
        for i in range(len(not_in_name)):
            list = ('AI_1', 'cor_1', not_in_name[i], not_in_time[i], 'True')
            input.append(list)
        print(input)
        # statement = "insert into attend values(:1,:2,:3, :4,:5)"
        curs.executemany("insert into attend(attend_id,course_id,stu_name,enter_time,ischeck) values(:1,:2,:3,:4,:5)",input)
        conn.commit()


else:
    print("파일 없음")
    os.mkdir(path)
    os.chdir(path)
    f = open('check.csv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f, delimiter='\t')
    data = {'Name': check_name, 'Time': check_time}
    dataframe = pd.DataFrame(data)
    print("들어온 사람: ",end="")
    print(check_name)
    print("들어온 시간: ",end="")
    print(check_time)
    dataframe.to_csv("check.csv", header=True, index=False)
    input =[]
    for i in range(len(check_name)):
        list = ('AI_1','cor_1',check_name[i], check_time[i],'True')
        input.append(list)
    print(input)
    #statement = "insert into attend values(:1,:2,:3, :4,:5)"
    curs.executemany("insert into attend(attend_id,course_id,stu_name,enter_time,ischeck) values(:1,:2,:3,:4,:5)",input)
    conn.commit()

f.close()
curs.close()

cv2.waitKey(0)
cv2.destroyAllWindows()