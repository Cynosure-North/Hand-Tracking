import cv2
import mediapipe as mp
import math
import numpy as np

# flags
claws = True
skeleton = True
dots = True
box = False
gesture_text = True
angle_text = False

# Setup stuff
capture = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 0.8, 0.5)
mpDraw = mp.solutions.drawing_utils



def unit_vector(vector):
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

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
    minX, maxX, minY, maxY = int(
        minX * w), int(maxX * w), int(minY * h), int(maxY * h)

    if box:
        img = cv2.rectangle(img, (minX - 7, minY - 7),
                            (maxX + 7, maxY + 7), (0, 0, 255), 2)

    # landmarks
    if skeleton and dots:
        mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    elif skeleton and not dots:
        mpDraw.draw_landmarks(img, mpHands.HAND_CONNECTIONS)
    elif not skeleton and dots:
        mpDraw.draw_landmarks(img, handLms)

    if claws:
        for id in enumerate(handLms.landmark):
            if id in (1, 2, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19):
                start = (handLms.landmark.x, handLms.landmark[id].y)
                end = vectorDiff2D(
                    *start, handLms.landmark[id + 1].x, handLms.landmark[id + 1].y, 1)
                img = cv2.line(img, (int(start[0] * w), int(start[1] * h)), (int(
                    end[0] + start[0] * w), int(end[1] + start[1] * h)), 2)
                print()
                print(math.sqrt(end[0]**2 + end[1]**2))

    if angle_text:
        for id, lm in enumerate(handLms.landmark):
            angle = jointAngle(id, handLms)
            cv2.putText(img, angle, (int(lm.x * w), int(lm.y * h)),
                        cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0))

    # text
    if gesture_text:
        cv2.putText(img, gesture, (minX - 5, minY - 10),
                    cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 0, 0))


def recogniseGesture(handLms):
    tiltDirection = 0
    # TODO: It doesn't work if it's side on
    gesture = ""
    for id, lm in enumerate(handLms.landmark):
        if id in (5, 9, 13, 17):
            tiltDirection += lm.z

    if tiltDirection < -0.3:
        gesture += "forward "
    elif tiltDirection > 0.1:
        gesture += "back "
    else:
        gesture += "upright "

    return gesture


def vectorDiff2D(x1, y1, x2, y2, scale=1):
    deltaX = (x2 - x1)
    deltaY = (y2 - y1)
    length = math.sqrt(deltaX ** 2 + deltaY ** 2)
    deltaX = (deltaX / length) * scale
    deltaY = (deltaY / length) * scale
    return (deltaX, deltaY)


def jointAngle(id, handLms):
    if id != 5 and id != 9 and id != 13 and id != 17:
        return
    pass


def fingerAngle(id, handLms):
    pass


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
