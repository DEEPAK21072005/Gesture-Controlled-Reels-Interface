import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False,
                       max_num_hands=1,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Start webcam
cap = cv2.VideoCapture(0)

# Cooldown timer
last_action_time = 0
action_delay = 1.97  # Slightly faster than 2 seconds

def is_thumbs_up(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP]
    middle_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]
    return (thumb_tip.y < index_mcp.y) and (thumb_tip.y < middle_mcp.y)

def is_open_palm(hand_landmarks):
    fingers_extended = []
    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]:
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[tip_id - 2]
        fingers_extended.append(tip.y < pip.y)
    return all(fingers_extended)

def is_fist(hand_landmarks):
    fingers_folded = []
    for tip_id in [mp_hands.HandLandmark.INDEX_FINGER_TIP,
                   mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
                   mp_hands.HandLandmark.RING_FINGER_TIP,
                   mp_hands.HandLandmark.PINKY_TIP]:
        tip = hand_landmarks.landmark[tip_id]
        pip = hand_landmarks.landmark[tip_id - 2]
        fingers_folded.append(tip.y > pip.y)
    return all(fingers_folded)

while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            current_time = time.time()
            if current_time - last_action_time > action_delay:

                if is_thumbs_up(hand_landmarks):
                    pyautogui.click(x=1821, y=726)  # Like
                    cv2.putText(frame, "Liked!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0), 2)
                    last_action_time = current_time

                elif is_open_palm(hand_landmarks):
                    pyautogui.scroll(-500)  # Scroll down
                    cv2.putText(frame, "Next Reel", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 0, 255), 2)
                    last_action_time = current_time

                elif is_fist(hand_landmarks):
                    pyautogui.scroll(500)  # Scroll up
                    cv2.putText(frame, "Previous Reel", (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (255, 0, 255), 2)
                    last_action_time = current_time

    cv2.imshow("Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
