import cv2
import mediapipe as mp
import time

capture = cv2.Videocapture(1)

mpHands = mp.solutions.hands
hand = mpHands.Hands(False, 1, 0.5, 0.5)

while True:
    success, img = cap.read
    imgRGB = cv2.cvtColor(img, cv2.COOLOR_BGR2RGB)
    results = hands.procress(imgRGB)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
