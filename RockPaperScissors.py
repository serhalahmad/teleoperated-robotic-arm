import cv2 as cv
import mediapipe as np

np_drawing = np.solutions.drawing_utils
np_drawing_styles = np.solutions.drawing_styles
np_hands = np.solutions.hands

'''
# in a cv window we go y positive downwards and x positive to the right thus when checking for the landmark y value,
# for rock we must get all the landmarks at the tips of the finger to be at a higher y value than the ones at the
# bottom for scissors only two landmarks suffice and anything else we consider to be paper
# this is what the following function does:
'''

def getHandMove(hand_landmarks):
    landmarks = hand_landmarks.landmark
    if all(landmarks[i].y < landmarks[i + 3].y for i in range(9, 20, 4)):
        return "rock"
    elif landmarks[13].y < landmarks[16].y and landmarks[17].y < landmarks[20].y:
        return "scissors"
    else:
        return 'paper'


vid = cv.VideoCapture(0)
clock = 0  # initializing the clock
p1_movve = p2_move = None
gameText = ""
success = True  # parameter to check if there are enough hands to play

with np_hands.Hands(model_complexity=0,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5) as hands:  # setting parameters for hand detection
    # adding the frame
    while True:
        ret, frame = vid.read()
        if not ret or frame is None: break  # incase no frame generated break out of the loop
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # since results need color in rgb convert to rgb
        results = hands.process(frame)  # get results
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)  # convert back to bgr

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                np_drawing.draw_landmarks(frame,
                                          hand_landmarks,
                                          np_hands.HAND_CONNECTIONS,
                                          np_drawing_styles.get_default_hand_landmarks_style(),
                                          np_drawing_styles.get_default_hand_connections_style())
                # show the finger connections and the landmarks on the frame

        if 0 <= clock < 20:
            success = True
            gameText = "Ready?"
        # before clock reaches 60 we count down for the players to get ready
        elif clock < 30:
            gameText = "3..."
        elif clock < 40:
            gameText = "2..."
        elif clock < 50:
            gameText = "1..."
        elif clock < 60:
            gameText = "GO!"
        # when clock reaches 60 we get the result of who won
        elif clock == 60:
            hls = results.multi_hand_landmarks
            if hls and len(hls) == 2:  # checks if both hands appear
                p1_movve = getHandMove(hls[0])
                p2_move = getHandMove(hls[1])
            else:  # if not set success as false
                success = False
        elif clock < 100:
            if success:
                # conditional for game rules and choose who wins
                gameText = f"Player1 played {p1_movve}. Player2 played {p2_move}."
                if p1_movve == p2_move:
                    gameText = f"{gameText} Game is tied."
                elif p1_movve == "paper" and p2_move == "rock":
                    gameText = f"{gameText} Player 1 wins"
                elif p1_movve == "rock" and p2_move == "scissors":
                    gameText = f"{gameText} Player1  wins"
                elif p1_movve == "scissors" and p2_move == "paper":
                    gameText = f"{gameText} Player1  wins"
                else:
                    gameText = f"{gameText} Player2 wins"
            else:
                gameText = "Didn't play properly!"

        cv.putText(frame, f"Clock: {clock}", (50, 50), cv.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2,
                   cv.LINE_AA)  # displaying clock value
        cv.putText(frame, gameText, (50, 80), cv.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2,
                   cv.LINE_AA)  # printing the output onto the screen
        clock = (clock + 1) % 100  # increment clock

        cv.imshow('frame', frame)

        if cv.waitKey(1) & 0xFF == ord('q'):
            break  # exit code once we press q to quit
