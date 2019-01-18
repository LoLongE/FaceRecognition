import cv2
import datetime
import warnings
import Function
import threading
import queue


# Basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        img = cv2.flip(frame, 1)
        check = 0
        my_q = queue.Queue()
        count = 1
        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(img, (0, 0), fx=2.0,  fy=2.0)
        cv2.imshow('Video', small_frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            tm = datetime.datetime.now()
            dir_time = tm.strftime('%Y-%m-%d %H-%M')
            image = dir_time + ".jpg"
            cv2.imwrite('%s' %image, small_frame)
            t= threading.Thread(target = Function.check_Person, args= (image,))
            t.start()

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()