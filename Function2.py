# DB Server http://192.168.0.154:8080
import face_recognition_api
import cv2
import os
import pickle
import datetime
import pymysql
import pandas as pd
import csv

def getTime(type_print):
    if type_print == 1:
        return datetime.datetime.now().strftime('%H:%M:%S')
    else:
        return datetime.datetime.now()

def makeDir(dir_name): #폴더를 생성
    path = "./"+dir_name
    if not os.path.isdir("%s" %path):
        os.mkdir("%s" %path)
    os.chdir("%s" % path)

def printInfo(now, now2, small_frame): #버튼을 눌러 저장한 이미지에 정보를 출력
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(small_frame , "Start:" + str(now),(20,50), font,1.0,(255,255,255),1)
    cv2.putText(small_frame , "End:" + str(now2),(20,100), font,1.0,(255,255,255),1)
    cv2.putText(small_frame , "Processing:  " + str(now2-now),(20,150), font,1.0,(255,255,255),1)
    cv2.putText(small_frame, "People: ", (20, 200), font, 1.0, (255, 255, 255), 1)

def print_log(check_name, check_time, not_in_name, not_in_time): #출석체크버튼 클릭시 인식된 사람 or 두번째 눌렀을때 새로 들어온 사람 확인여부 출력
    print("들어온 사람: ", end="")
    print(check_name)
    print("들어온 시간: ", end="")
    print(check_time)
    if len(not_in_name) >0:
        print("추가로 들어온 사람: ", end="")
        print(not_in_name)
        print("들어온 시간: ", end="")
        print(not_in_time)

def send_query(curs, conn, query, enroll_list , c_time, dir_time): #mysql에 쿼리문을 보내서 attend 테이블에 정보 입력
    input = []
    std = datetime.datetime.strptime('1900-01-01 17:45:00', '%Y-%m-%d %H:%M:%S') #사람이 인식됬을때의 시간을 문자열로 바꾼것을 다시 시간으로 바꾸고 그것을 수업시간과 비교
    for i in range(len(enroll_list)):
        strToTime = datetime.datetime.strptime(c_time[i], '%H:%M:%S')
        if strToTime > std:
            list = (enroll_list[i], c_time[i], dir_time ,'late')
            input.append(list)
        else:
            list = (enroll_list[i], c_time[i], dir_time, 'attend')
            input.append(list)
    print(input)
    curs.executemany(query,input)
    conn.commit()

def check_Person(image):
    # query를 이용해 db에서 정보 얻어옴
    conn = pymysql.connect(host="localhost",  # your host, usually localhost
                           user="root",  # your username
                           passwd="54321",  # your password
                           db="TEST",
                           charset='utf8')  # name of the data base
    curs = conn.cursor()
    curs.execute("select stu_name from student,enroll where student.stu_id = enroll.stu_id and course_id = 'cor_1'") #cor_1 과목을 기준으로 수업듣는 학생의 이름 받아옴
    result = curs.fetchall()

    name_result = [] #db에 있는 학생의 이름 가져오기위해
    check_time = [] #들어온 시간 출력
    check_name = [] #출석이 된 학생의 이름 받아오기 위해
    not_in_name = [] #새로 들어온 사람의 이름을 받기 위해
    not_in_time=[] #새로 들어온 사람의 시간을 받기 위해
    enroll_list = []

    for i in range(len(result)): #db에서 학생의 이름만 받아옴
         name_result.append(result[i][0])

    now = getTime(0)
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
    small_frame = cv2.imread("%s" %image)

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
        check_time.append(getTime(1))  # 인식됐을때의 시간 저장
        check_name.append(name)  # 검출된 사람의 이름 저장

    now2 = getTime(0)
    printInfo(now,now2,small_frame)

    for i in range(len(predictions)): #전체 사진에서 검출된 사람의 이름 전부 출력
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(small_frame , predictions[i][0],( (i*120)+ 160 ,200), font,1.0,(255,255,255),1)

    tm = getTime(0)
    dir_time= tm.strftime('%Y-%m-%d')
    dir_time2 = tm.strftime('%Y-%m-%d %H-%M')
    makeDir(dir_time)
    path = os.getcwd() + "/cor_1"

    #해당날짜에 해당하는 폴더가 있으면 기존 폴더를 열어서 처음 검출된 학생의 이름과 시간만 csv파일에 저장
    if os.path.isdir(path):
        print("파일 있당")
        os.chdir(path)
        cv2.imwrite('%s.jpg' %dir_time2, small_frame)
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
        for i in range(len(not_in_name)):
            sql = "select enroll_id from student,enroll where student.stu_id = enroll.stu_id and student.stu_name = %s and course_id = 'cor_1'" #검출된 학생 중 cor_1의 수업을 듣는 학생의 enroll_id 를 받아옴
            val = not_in_name[i]
            curs.execute(sql, val)
            for row in curs.fetchall():
                enroll_list.append(row[0])
        if len(not_in_name) >0 :
            send_query(curs,conn,"insert into attend(enroll_id, enter_time, enter_date, ischeck) values(%s, %s, %s, %s)",enroll_list, not_in_time, dir_time)

    else:
        print("파일 없음")
        makeDir("cor_1")
        cv2.imwrite('%s.jpg' %dir_time2, small_frame)
        f = open('check.csv', 'w', encoding='utf-8', newline='')
        wr = csv.writer(f, delimiter='\t')
        data = {'Name': check_name, 'Time': check_time}
        dataframe = pd.DataFrame(data)
        print_log(check_name, check_time, not_in_name, not_in_time)
        dataframe.to_csv("check.csv", header=True, index=False)
        for i in range(len(check_name)):
            sql = "select enroll_id from student,enroll where student.stu_id = enroll.stu_id and student.stu_name = %s and course_id = 'cor_1'"
            val = check_name[i]
            curs.execute(sql, val)
            for row in curs.fetchall():
                enroll_list.append(row[0])
        send_query(curs, conn, "insert into attend(enroll_id, enter_time, enter_date, ischeck) values(%s, %s, %s, %s)", enroll_list , check_time, dir_time)

    f.close()
    curs.close()
    conn.close()

    cv2.waitKey(0)
    cv2.destroyAllWindows()