import cv2
import face_recognition
import os

dir_path = "C:/ProgramData/Anaconda3/Lib/idlelib"
dir_name = "save_img"
path = dir_path + "/"+dir_name + "/"

if not os.path.isdir(path):
    os.mkdir(path)
   

os.chdir(path)

vidcap = cv2.VideoCapture(0)
count = 0
face_locations = []
crop_img=[]

while (vidcap.isOpened()):
    
    ret, image = vidcap.read()
    img = cv2.flip(image, 1)

    face_locations = face_recognition.face_locations(img)
    
    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(img, (left, top), (right, bottom), (0, 0, 255), 2)
        crop_img = img[top:bottom, left:right]
        
    cv2.imshow('video',img)
    
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
            # 캡쳐된 이미지를 저장하는 함수 
        cv2.imwrite("frame%d.jpg" % count, crop_img)

        print('Saved frame%d.jpg' % count)
        count += 1


vidcap.release()
