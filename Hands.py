import cv2
import mediapipe as mp

capture = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(False, 2, 0.5, 0.5)
mpDraw = mp.solutions.drawing_utils

success, img = capture.read()
h, w, c = img.shape

def recogniseGesture(img):
    return "hand"

while True:
    success, img = capture.read()
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
s
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            minX, maxX, minY, maxY = w, 0, h, 0
            mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
            for lm in handLms.landmark:
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
