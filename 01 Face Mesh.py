import cv2
import mediapipe as mp
import numpy

capture = cv2.VideoCapture(0)
mpFace = mp.solutions.face_mesh
face = mpFace.FaceMesh(False, 1, 0.5, 0.5)
mpDraw = mp.solutions.drawing_utils

def recogniseGesture(img):
    return "face"

while True:
    success, img = capture.read()
    h, w, c = img.shape
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = face.process(imgRGB)


    if results.multi_face_landmarks:
        for faceLms in results.multi_face_landmarks:
            minX, maxX, minY, maxY = w, 0, h, 0
            mpDraw.draw_landmarks(img, faceLms, mpFace.FACE_CONNECTIONS, mpDraw.DrawingSpec(mpDraw.RED_COLOR, 1, 1), mpDraw.DrawingSpec((0,255, 0), 2, 1))
            for lm in faceLms.landmark:
                if lm.x > maxX:
                    maxX = lm.x
                if lm.x < minX:
                    minX = lm.x
                if lm.y > maxY:
                    maxY = lm.y
                if lm.y < minY:
                    minY = lm.y
            minX, maxX, minY, maxY, = int(minX*w), int(maxX*w), int(minY*h), int(maxY*h)
            img = cv2.rectangle(img, (minX-7, minY-7), (maxX+7, maxY+7), (0, 0, 255), 2)
            gesture = recogniseGesture(img)
            cv2.putText(img, gesture, (minX-5, minY-10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0), )
        
    cv2.imshow("Image", img)
    cv2.waitKey(1)
