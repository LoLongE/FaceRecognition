# DB Server http://192.168.0.154:8080
import face_recognition_api
import cv2
import os
import pickle
import datetime
import cx_Oracle
import pandas as pd
import csv

def getTime(type_print):
    if type_print == 1:
        return datetime.datetime.now().strftime('%Y-%m-%d %H-%M')
    else:
        return datetime.datetime.now()

def makeDir(dir_name):
    path = "./"+dir_name
    if not os.path.isdir("%s" %path):
        os.mkdir("%s" %path)
    os.chdir("%s" % path)

def printInfo(now, now2):
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame , "Start:" + str(now),(20,50), font,1.0,(255,255,255),1)
    cv2.putText(small_frame , "End:" + str(now2),(20,100), font,1.0,(255,255,255),1)
    cv2.putText(small_frame , "Processing:  " + str(now2-now),(20,150), font,1.0,(255,255,255),1)
    cv2.putText(small_frame, "People: ", (20, 200), font, 1.0, (255, 255, 255), 1)

def print_log(check_name, check_time, not_in_name, not_in_time):
    print("들어온 사람: ", end="")
    print(check_name)
    print("들어온 시간: ", end="")
    print(check_time)
    if len(not_in_name) >0:
        print("추가로 들어온 사람: ", end="")
        print(not_in_name)
        print("들어온 시간: ", end="")
        print(not_in_time)

def send_query(curs, conn, query, c_name, c_time):
    input = []
    #if len(not_in_name) >0 :
    for i in range(len(c_name)):
        list = ('AI_1', 'cor_1', c_name[i], c_time[i], 'True')
        input.append(list)
    print(input)
    curs.executemany(query,input)
    conn.commit()

# query를 이용해 db에서 정보 얻어옴
connstr = "test/test"
conn = cx_Oracle.connect(connstr)
curs = conn.cursor()
curs.execute("select name from enroll, student where enroll.stu_id = student.stu_id and enroll.course_id = 'cor_1'")
result = curs.fetchall()

name_result = [] #db에 있는 학생의 이름 가져오기위해
check_time = [] #들어온 시간 출력
check_name = [] #출석이 된 학생의 이름 받아오기 위해
not_in_name = [] #새로 들어온 사람의 이름을 받기 위해
not_in_time=[] #새로 들어온 사람의 시간을 받기 위해

for i in range(len(result)): #db에서 학생의 이름만 받아옴
     name_result.append(result[i][0])

now = getTime(0)
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

# 촬영된 영상을 한장의 사진으로 받아옴
small_frame = cv2.imread("./test-images/test04/84.jpg")

# 사진 이미지를 resize
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
    # 인식된 얼굴에 사각형 출력
    cv2.rectangle(small_frame, (left, top), (right, bottom), (0, 0, 255), 2)
    #사각형밑에 라벨이 출력되도록
    cv2.rectangle(small_frame, (left, bottom - 15), (right, bottom), (0, 0, 255), cv2.FILLED)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
    check_time.append(datetime.datetime.now().strftime('%Y-%m-%d %H-%M'))  # 인식됐을때의 시간 저장
    check_name.append(name)  # 검출된 사람의 이름 저장

now2 = getTime(0)
printInfo(now,now2)

for i in range(len(predictions)): #전체 사진에서 검출된 사람의 이름 전부 출력
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame , predictions[i][0],( (i*120)+ 160 ,200), font,1.0,(255,255,255),1)

# Display the resulting image
cv2.imshow('Video', small_frame)

tm = datetime.datetime.now()
dir_time= tm.strftime('%Y-%m-%d')

path = makeDir(dir_time)
cv2.imwrite('%s.jpg' % "image_name", small_frame)

path = os.getcwd() + "/cor_1"

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
    print_log(check_name, check_time, not_in_name, not_in_time)
    data = {'Name': not_in_name, 'Time': not_in_time}
    dataframe = pd.DataFrame(data)
    dataframe.to_csv("check.csv", mode='a',header=False, index=False)
    if len(not_in_name) >0 :
        send_query(curs,conn,"insert into attend(attend_id,course_id,stu_name,enter_time,ischeck) values(:1,:2,:3,:4,:5)",not_in_name, not_in_time)

else:
    print("파일 없음")
    makeDir("cor_1")
    f = open('check.csv', 'w', encoding='utf-8', newline='')
    wr = csv.writer(f, delimiter='\t')
    data = {'Name': check_name, 'Time': check_time}
    dataframe = pd.DataFrame(data)
    print_log(check_name, check_time, not_in_name, not_in_time)
    dataframe.to_csv("check.csv", header=True, index=False)
    send_query(curs, conn, "insert into attend(attend_id,course_id,stu_name,enter_time,ischeck) values(:1,:2,:3,:4,:5)",  check_name, check_time)

f.close()
curs.close()

cv2.waitKey(0)
cv2.destroyAllWindows()