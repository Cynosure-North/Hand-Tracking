import cv2
import mediapipe as mp
import math
import numpy as np

# flags
claws = True
skeleton = True
dots = True
box = True
gesture_text = True
joint_text = False
finger_text = False
text_on_side = False
degrees = True

# Setup stuff
capture = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 0.8, 0.5)
mpDraw = mp.solutions.drawing_utils

def drawDebug(handLms, img):

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
    minX, maxX, minY, maxY = int(minX * w), int(maxX * w), int(minY * h), int(maxY * h)

    if box:
        img = cv2.rectangle(img, (minX - 7, minY - 7),(maxX + 7, maxY + 7), (0, 0, 255), 2)

    # landmarks
    if skeleton and dots:
        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    elif skeleton and not dots:
        mpDraw.draw_landmarks(img, mpHands.HAND_CONNECTIONS)
    elif not skeleton and dots:
        mpDraw.draw_landmarks(img, handLms)

    if claws:
        for id in range(len(handLms.landmark)):
            if id in (1,2,3, 5,6,7, 9,10,11, 13,14,15, 17,18,19):
                start = (handLms.landmark[id].x, handLms.landmark[id].y, handLms.landmark[id].z)
                end = vectorBetween(*start, handLms.landmark[id + 1].x, handLms.landmark[id + 1].y, handLms.landmark[id + 1].z, 0.2)
                img = cv2.line(img, (int(start[0] * w), int(start[1] * h)), (int((end[0] + start[0]) * w), int((end[1] + start[1]) * h)), 2)

    if joint_text:
        for id in range(len(handLms.landmark)):
            angle = jointAngle(id, handLms)

            if angle != None:
                angle = "{:.2f}".format(jointAngle(id, handLms))
            else:
                angle = ""

            if not text_on_side:
                cv2.putText(img, angle, (int(handLms.landmark[id].x * w), int(handLms.landmark[id].y * h)),cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
            else:
                pass

    if finger_text:
        for id in (8,12,16,20):
            angle = fingerAngle(id, handLms)

            if angle != None:
                angle = "{:.2f}".format(fingerAngle(id, handLms))
            else:
                angle = ""

            if not text_on_side:
                cv2.putText(img, angle, (int(handLms.landmark[id].x * w), int(handLms.landmark[id].y * h)),cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))
            else:
                pass

        #TODO: Thumb angle

    # text
    if gesture_text:
        gesture = recogniseGesture(handLms)
        cv2.putText(img, gesture, (minX - 5, minY - 10),cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0))

def recogniseGesture(handLms):
    #TODO: It doesn't work if it's side on
    gesture = ""

    gesture += palmDirection(handLms)

def palmDirection(handLms):
    direction = ""
    tiltDirection = 0
    for id, lm in enumerate(handLms.landmark):
        if id in (5, 9, 13, 17):
            tiltDirection += lm.z

    if tiltDirection < -0.3:
        direction += "forward "
    elif tiltDirection > 0.1:
        direction += "back "
    else:
        direction += "upright "

    return direction


def vectorBetween(x1, y1, z1, x2, y2, z2, scale=1):
    deltaX = (x2 - x1)
    deltaY = (y2 - y1)
    deltaZ = (z1 - z2)
    length = math.sqrt(deltaX**2 + deltaY**2 + deltaZ**2)
    x = (deltaX / length) * scale
    y = (deltaY / length) * scale
    z = (deltaZ / length) * scale
    return (x, y, z)

def nornalisedVector(x, y ,z=0):
    length = math.sqrt(x**2 + y**2 + z**2)
    return (x/length, y/length, z/length)


def angle_between(x1,y1,z1, x2,y2,z2):
    v1_u = nornalisedVector(x1,y1,z1)
    v2_u = nornalisedVector(x2,y2,z2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def jointAngle(id, handLms):
    if id not in (2,3, 5,6,7, 9,10,11, 13,14,15, 17,18,19):
        return
    if id in (1,5,9,13,17):
        p1 = (handLms.landmark[0].x, handLms.landmark[0].y, handLms.landmark[0].z)
    else:
        p1 = (handLms.landmark[id-1].x, handLms.landmark[id-1].y, handLms.landmark[id-1].z)
    p2 = (handLms.landmark[id].x, handLms.landmark[id].y, handLms.landmark[id].z)
    p3 = (handLms.landmark[id+1].x, handLms.landmark[id+1].y, handLms.landmark[id+1].z)
    v1 = vectorBetween(*p1, *p2)
    v2 = vectorBetween(*p2, *p3)
    angle = angle_between(*v1, *v2)
    if degrees:
        return angle * (180/math.pi)
    else:
        return angle

def fingerAngle(id, handLms):
    if id not in ( 8,12,16,20):
        return
    else:
        total = 0
        for i in range(1,4):
            total += jointAngle(id-i, handLms)
        return total

while True:
    try:
        success, img = capture.read()
        h, w, c = img.shape
    except:
        print("Camera Error")
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            gesture = recogniseGesture(handLms)

            drawDebug(handLms, img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
