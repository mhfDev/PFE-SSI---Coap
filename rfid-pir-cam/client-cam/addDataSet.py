from cv2 import cv2
import sqlite3,time

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
con = sqlite3.connect("imEtudiants.db")
c = con.cursor()

nom=str(input("Nom : "))
prenom=str(input("Prenom : "))
uid=str(input("UID : "))

c.execute('INSERT INTO etudiants (uid,nom,prenom) VALUES ("'+uid+'","'+nom+'","'+prenom+'")')
con.commit()

c.execute('SELECT id FROM etudiants ORDER BY id DESC LIMIT 1')
Id = c.fetchone()[0]
con.close()

print("Id = ", Id)
video_capture = cv2.VideoCapture(0)

img_counter = 0

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    k = cv2.waitKey(1)
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.5,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('FaceDetection', frame)
    if k%256 == 27: #ESC Pressed
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "dataSet/User."+str(Id) +".{}.jpg".format(img_counter)
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        img_counter += 1
# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()


