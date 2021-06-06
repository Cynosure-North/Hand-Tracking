import cv2
import mediapipe as mp
import math

capture = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 0.8, 0.5)
mpDraw = mp.solutions.drawing_utils

def recogniseGesture(handLms):
    tiltDirection = 0
    #TODO: It doesn't work if it's side on
    gesture = ""
    for id, lm in enumerate(handLms.landmark):
        if id in (5,9,13,17):
            tiltDirection += lm.z

    if tiltDirection < -0.3:
        gesture += "forward "
    elif tiltDirection > 0.1:
        gesture += "back "
    else:
        gesture += "upright "
        
    return gesture

def getFingerCurl(id, handLms):
    if id!=5 and id!=9 and id!=13 and id!=17:
        return 0
    normalX = (handLms.landmark[0].x - handLms[id].x)**2
    normalY = (handLms.landmark[0].y - handLms[id].y)**2
    normalZ = (handLms.landmark[0].x - handLms[id].z)**2
    for i in range(id, 4):
        pass

while True: 
    try:
        success, img = capture.read()
        h, w, c = img.shape
    except:
        print("Cammera Error")
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            gesture = recogniseGesture(handLms)


            #Debug Draw
            #landmarks
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            minX, maxX, minY, maxY = w, 0, h, 0
            for id, lm in enumerate(handLms.landmark):
                if lm.x > maxX:
                    maxX = lm.x
                if lm.x < minX:
                    minX = lm.x
                if lm.y > maxY:
                    maxY = lm.y
                if lm.y < minY:
                    minY = lm.y

                if id in (1,2,3,5,6,7,9,10,11,13,14,15,17,18,19):
                    #claw
                    start = (handLms.landmark[id].x, handLms.landmark[id].y)
                    end = (handLms.landmark[id+1].x, handLms.landmark[id+1].y)
                    deltaX = (end[0]-start[0])
                    deltaY = (end[1]-start[1])
                    length = math.sqrt(deltaX**2 + deltaY**2)
                    deltaX = (deltaX / length) * 0.2
                    deltaY = (deltaY / length) * 0.2
                    end = (start[0] + deltaX, start[1] + deltaY)
                    img = cv2.line(img, (int(start[0]*w), int(start[1]*h)), (int(end[0]*w), int(end[1]*h)), 2)

            minX, maxX, minY, maxY= int(minX*w), int(maxX*w), int(minY*h), int(maxY*h)
            #bounding box
            img = cv2.rectangle(img, (minX-7, minY-7), (maxX+7, maxY+7), (0, 0, 255), 2)
            #text
            cv2.putText(img, gesture, (minX-5, minY-10), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0))

                    
    cv2.imshow("Image", img)
    cv2.waitKey(1)
