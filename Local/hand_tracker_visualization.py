
import cv2
import mediapipe
import os
from typing import Optional

class HandTrackerVisualization:
    def __init__(self):
        self.mp_drawing = mediapipe.solutions.drawing_utils
        self.mp_hands = mediapipe.solutions.hands
        self.landmark_drawing_spec = mediapipe.solutions.drawing_utils.DrawingSpec( color = (255, 0, 255), thickness = 4, circle_radius = 2)
        self.connection_drawing_spec = mediapipe.solutions.drawing_utils.DrawingSpec(color = (20, 180, 90), thickness = 2, circle_radius = 2)
    
    def visualize_hand_landmarks(self, hand_landmarks : dict, original_video_path: str, output_video_path : str):
        """Esta función toma el diccionario de coordenadas de los puntos clave de las manos detectadas en cada frame y 
        crea un nuevo video donde se visualicen las manos detectadas por frame.
        """
        
        VR = cv2.VideoCapture(original_video_path); # video reader
        width  = int(VR.get(cv2.CAP_PROP_FRAME_WIDTH));   # float `width`
        height = int(VR.get(cv2.CAP_PROP_FRAME_HEIGHT));  # float `height`
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        fps = VR.get(cv2.CAP_PROP_FPS)
        VW = cv2.VideoWriter('out.mp4', fourcc, fps, (height,width)) # video writer
        total_processed_time_ms = max(hand_landmarks.keys(), default=-1) + 1

        while(VR.isOpened()):
            ret, Frame = VR.read()
            if ret == True:
                current_timestamp_ms = int(round(VR.get(cv2.CAP_PROP_POS_MSEC)))
                if current_timestamp_ms >= total_processed_time_ms:
                    break
                if current_timestamp_ms in hand_landmarks:
                    for hand_lms in hand_landmarks[current_timestamp_ms]: # imprime los puntos claves
                        self.mp_drawing.draw_landmarks(Frame, hand_lms, self.mp_hands.HAND_CONNECTIONS, landmark_drawing_spec = self.landmark_drawing_spec, connection_drawing_spec = self.connection_drawing_spec)

                Frame = cv2.rotate(Frame, cv2.ROTATE_90_CLOCKWISE)
                VW.write(Frame)
            else:
                break

        VR.release()
        VW.release()

        os.system(f"ffmpeg -i out.mp4 -vcodec h264 {output_video_path}")
        os.system("rm out.mp4")

