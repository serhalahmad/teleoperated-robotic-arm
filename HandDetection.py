import mediapipe as mp
import cv2
import numpy as np
import serial

# Initialize the serial to send data to the Arduino
mySerial = serial.Serial('COM3', 9600)
mySerial.close()
mySerial.open()

temp = [];

# Detect whether left or right hand
# index is the hand result (if we have multiple hands shown up)
# hand contains the hand landmarks
# results contains all the detections


def get_label(index, hand, results):
    output = None

    # Loop through the detected hands
    for idx, classification in enumerate(results.multi_handedness):

        if classification.classification[0].index == index:
            # Process Results
            label = classification.classification[0].label  # detect whether left or right
            score = classification.classification[0].score  # detect the degree of confidence of the label
            text = '{} {}'.format(label, round(score, 2))  # format the text to be displayed

            # Extract Coordinates of where to display the text
            coords = tuple(np.multiply(
                np.array((hand.landmark[mp_hands.HandLandmark.WRIST].x, hand.landmark[mp_hands.HandLandmark.WRIST].y)),
                [640, 480]).astype(int))

            output = text, coords
    return output


def draw_finger_angles(image, results, joint_list):
    # Loop through hands
    for hand in results.multi_hand_landmarks:
        # Loop through joint sets
        for joint in joint_list:
            a = np.array([hand.landmark[joint[0]].x, hand.landmark[joint[0]].y])  # First Coord
            b = np.array([hand.landmark[joint[1]].x, hand.landmark[joint[1]].y])  # Second Coord
            c = np.array([hand.landmark[joint[2]].x, hand.landmark[joint[2]].y])  # Third Coord

            # Calculating the angle
            radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
            angle = np.abs(radians * 180.0 / np.pi)

            if angle > 180.0:
                angle = 360 - angle
            temp.append(angle)

            # Displaying the angle
            cv2.putText(image, str(round(angle, 2)), tuple(np.multiply(b, [640, 480]).astype(int)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)
    return image, temp


mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

joint_list = [[4, 2, 1], [8, 6, 5], [12, 10, 9], [16, 14, 13], [20, 18, 17]]
cap = cv2.VideoCapture(1)  # start the video feed

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        ret, frame = cap.read()

        # BGR 2 RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Flip on horizontal
        image = cv2.flip(image, 1)
        # Set flag
        image.flags.writeable = False  # stop copying the image
        # Detections
        results = hands.process(image)
        # Set flag to true
        image.flags.writeable = True  # start copying the image
        # RGB 2 BGR
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Rendering results
        if results.multi_hand_landmarks:
            for num, hand in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                                          mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2),
                                          )

                # Render left or right detection
                if get_label(num, hand, results):  # Checking if we actually have a result
                    text, coord = get_label(num, hand, results)
                    cv2.putText(image, text, coord, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # Draw angles to image from joint list
            draw_finger_angles(image, results, joint_list)

            # Preparing the data to be sent to the Arduino
            fingers = temp;
            temp = [];

            # scaling the values between 0 and 10
            for i in range(5):
                fingers[i] = int(fingers[i] * 10 / 180)
            arduinoFingers = "$"
            for i in fingers:
                arduinoFingers += str(i)
            mySerial.write(arduinoFingers.encode())  # Sending the data to Arduino
            print(arduinoFingers)

        cv2.imshow('Hand Tracking', image)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
