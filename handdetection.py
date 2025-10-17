import cv2
import mediapipe as mp
from pygamevideowindow import play_video_window
import threading
import time

cap = cv2.VideoCapture(0)

# Initialize MediaPipe for hands detection
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# Juggling motion detection variables
juggling_state = {
    'last_up_hand': None,  # 'left' or 'right'
    'alternating_count': 0,
    'last_gesture_time': time.time(),
    'video_playing': False
}

# Function to recognize hand gestures
def recognize_gesture(hand_landmarks, handedness):
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # centroid of the hand (normalized coordinates)
    xs = [lm.x for lm in hand_landmarks.landmark]
    ys = [lm.y for lm in hand_landmarks.landmark]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    # determine which hand (left/right)
    hand_label = handedness.classification[0].label.lower()

    # persistent storage across calls (keeps last positions for each hand)
    if not hasattr(recognize_gesture, 'prev_positions'):
        recognize_gesture.prev_positions = {}
    
    prev_positions = recognize_gesture.prev_positions

    # thresholds
    MOVEMENT_THRESHOLD = 0.02   # vertical movement threshold (normalized)

    # check if we have previous position for this hand
    if hand_label not in prev_positions:
        prev_positions[hand_label] = {'x': cx, 'y': cy}
        return "Stationary", hand_label

    # determine vertical movement: note MediaPipe y increases downward
    dy = prev_positions[hand_label]['y'] - cy
    prev_positions[hand_label] = {'x': cx, 'y': cy}

    if dy > MOVEMENT_THRESHOLD:
        return "Moving Up", hand_label
    elif dy < -MOVEMENT_THRESHOLD:
        return "Moving Down", hand_label
    else:
        return "Stationary", hand_label

def detect_juggling_motion(gesture, hand_label):
    """Detect alternating upward hand movements (juggling pattern)"""
    current_time = time.time()
    
    if gesture == "Moving Up":
        # Check if this is a different hand than the last one that moved up
        if (juggling_state['last_up_hand'] is not None and 
            juggling_state['last_up_hand'] != hand_label and
            current_time - juggling_state['last_gesture_time'] < 2.0):  # Within 2 seconds
            
            juggling_state['alternating_count'] += 1
            print(f"Alternating motion detected! Count: {juggling_state['alternating_count']}")
        else:
            # Same hand or too much time passed, reset counter
            juggling_state['alternating_count'] = 1
        
        juggling_state['last_up_hand'] = hand_label
        juggling_state['last_gesture_time'] = current_time
        
        # Trigger video if we have enough alternating motions
        if (juggling_state['alternating_count'] >= 4 and 
            not juggling_state['video_playing']):
            print("Juggling motion detected! Starting video...")
            juggling_state['video_playing'] = True
            juggling_state['alternating_count'] = 0  # Reset counter
            
            def video_wrapper():
                try:
                    play_video_window()
                except Exception as e:
                    print(f"Error playing video: {e}")
                finally:
                    juggling_state['video_playing'] = False
            
            video_wrapper()

while True:
    success, img = cap.read()
    if not success:
        break

    # Convert the image to RGB for MediaPipe
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Process the image and detect hands
    results = hands.process(img_rgb)

    # If hands are detected, draw landmarks and recognize gestures
    if results.multi_hand_landmarks and results.multi_handedness:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture, hand_label = recognize_gesture(hand_landmarks, handedness)
            
            # Display gesture and hand info
            y_offset = 70 if hand_label == 'left' else 100
            cv2.putText(img, f"{hand_label}: {gesture}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Detect juggling motion
            detect_juggling_motion(gesture, hand_label)
    
    # Display juggling counter
    cv2.putText(img, f"Alternating count: {juggling_state['alternating_count']}", 
               (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("6 7", img)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()
