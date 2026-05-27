import cv2, mediapipe, os

mp_drawing = mediapipe.solutions.drawing_utils;
mp_hands = mediapipe.solutions.hands;
landmark_drawing_spec = mediapipe.solutions.drawing_utils.DrawingSpec( color = (255, 0, 255), thickness = 4, circle_radius = 2);
connection_drawing_spec = mediapipe.solutions.drawing_utils.DrawingSpec(color = (20, 180, 90), thickness = 2, circle_radius = 2);

def HandDetector(Frame):
  with mp_hands.Hands(min_detection_confidence = 0.8, min_tracking_confidence = 0.5) as hands:
    img = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB) # conversion de espacio de color
    detected_image = hands.process(img) # deteccion de la(s) manos
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if detected_image.multi_hand_landmarks:
      for hand_lms in detected_image.multi_hand_landmarks: # imprime los puntos claves
        mp_drawing.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS, landmark_drawing_spec = landmark_drawing_spec, connection_drawing_spec = connection_drawing_spec )
  return img

VR = cv2.VideoCapture('SALUDO_COMPLET0_FRONTAL.mp4'); # video reader
width  = int(VR.get(cv2.CAP_PROP_FRAME_WIDTH)+0.5);   # float `width`
height = int(VR.get(cv2.CAP_PROP_FRAME_HEIGHT)+0.5);  # float `height`
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
VW = cv2.VideoWriter('out.mp4', fourcc, 20.0, (width,height));

k = 0;

while(VR.isOpened()):
  ret, Frame = VR.read()
  if ret == True:
    img = HandDetector(Frame)
    VW.write(img)

  k += 1;

  if k > 500:
    break

VR.release()
VW.release()

os.system("ffmpeg -i out.mp4 -vcodec h264 new.mp4")
os.system("rm out.mp4")
