import cv2
import mediapipe as mp
import pyautogui
import numpy as np

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
# Screen resolution
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.5) as hands:

    while True:
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            # Index finger tip landmark
            index_tip = hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip=hand.landmark[mp_hands.HandLandmark.THUMB_TIP]
            middle_tip=hand.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
            little_tip=hand.landmark[mp_hands.HandLandmark.PINKY_TIP]
            index_dip=hand.landmark[mp_hands.HandLandmark.INDEX_FINGER_DIP]
            ring_tip=hand.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]

            # Calculate distances

            dist=np.hypot((thumb_tip.x-index_tip.x),(thumb_tip.y-index_tip.y))
            dist1=np.hypot((thumb_tip.x-middle_tip.x),(thumb_tip.y-middle_tip.y))
            dist2=np.hypot((thumb_tip.x-little_tip.x),(thumb_tip.y-little_tip.y ))
            dist3=np.hypot((thumb_tip.x-index_dip.x),(thumb_tip.y-index_dip.y ))
            dist4=np.hypot((thumb_tip.x-ring_tip.x),(thumb_tip.y-ring_tip.y ))


            # Convert to screen coordinates
            x = int(index_tip.x * screen_w)
            y = int(index_tip.y * screen_h)

            if results.multi_hand_landmarks:
                for num, hand in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS, 
                                            mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                            mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                                            )

            # Move mouse
            pyautogui.moveTo(x, y)

            #other functions

            if dist < 0.03:
                pyautogui.click()
                print("click")
            elif dist1 < 0.03:
                pyautogui.rightClick()
                print("right click")
            elif dist3 < 0.03:
                pyautogui.typewrite(['ctrl','a'])
                print("selected all")
            elif dist2 < 0.03:
                pyautogui.typewrite(['ctrl','c'])
                print("copied")
            elif dist4<0.03:
                pyautogui.typewrite(['ctrl','v'])
                print("pasted")
            



        cv2.imshow("Hand Mouse Control", frame)
        if cv2.waitKey(10) & 0xFF == ('q'): 
            break

cap.release()
cv2.destroyAllWindows()
