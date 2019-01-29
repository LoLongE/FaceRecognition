import cv2
import datetime
import warnings
import Function2
import threading

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        img = cv2.flip(frame, 1)
        # Resize frame of video to 2 size for faster face recognition processing
        small_frame = cv2.resize(img, (0, 0), fx=2.0,  fy=2.0)

        # Hit 'q' on the keyboard to quit!
        k = cv2.waitKey(1)
        if  k == ord('q'):
            tm = datetime.datetime.now()
            dir_time = tm.strftime('%Y-%m-%d %H-%M')
            image = dir_time + ".jpg"
            cv2.imwrite('%s' %image, small_frame)
            t= threading.Thread(target = Function2.check_Person,
                                args= (image,))
            t.start()

        if k == 27:
            break

        cv2.imshow('Video', small_frame)
    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
