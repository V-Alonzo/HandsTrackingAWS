import cv2
import mediapipe as mp
import VM.video_getter as video_getter

class HandTracker:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands
    
        self.landmark_drawing_spec = self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=4)
        self.connection_drawing_spec = self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)


    def detect_hands(self, Frame):
        """
        Esta función detecta las manos en un frame dado utilizando MediaPipe Hands y devuelve las coordenadas de los puntos clave de las manos detectadas.
        """
        
        with self.mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5) as hands:
            img = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB) # conversion de espacio de color
            detected_image = hands.process(img) # deteccion de la(s) manos
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

            if detected_image.multi_hand_landmarks:
                return detected_image.multi_hand_landmarks
            return None
        
    def get_hands_landmarks(self, duration_ms: int, bucket_name: str, object_key: str):
        """Esta función abre el video desde S3 utilizando video_getter, 
        procesa cada frame para detectar las manos y 
        devuelve un diccionario donde cada key corresponde a un frame del video y 
        contiene las coordenadas de los puntos clave de las manos detectadas en ese frame.
        """
        with video_getter.build_default_video_getter(bucket_name=bucket_name, object_key=object_key) as video_getter_instance:
            # Cada key en este diccionario corresponde a un frame del video y contiene las coordenadas de los puntos clave de las manos detectadas en ese frame.
            landmarks = {}

            for i, frame in enumerate(video_getter_instance.frames()):
                current_timestamp_ms = video_getter_instance.current_timestamp_ms()
                if duration_ms is not None and current_timestamp_ms >= duration_ms:
                    break
                
                hand_landmarks = self.detect_hands(frame)

                if hand_landmarks is not None:
                    landmarks[current_timestamp_ms] = hand_landmarks

            return landmarks