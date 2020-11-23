from cv2 import cv2
import time

#returns path to photo for later use in facerec
def takeShot():
    cam = cv2.VideoCapture(0)
    for i in range(2):
        s, img = cam.read()
        time.sleep(1)
    if s:
        cv2.imwrite("photo/shot.jpg",img) #save image
    
    cam.release()
    print("photo taken")    
    return "photo/shot.jpg"
