import Local.video_uploader as video_uploader

import VM.hand_tracker as hand_tracker

from Local.hand_tracker_visualization import HandTrackerVisualization

import Local.configurations as configurations

path_in_s3 = video_uploader.upload_video_to_s3(
    file_path = configurations.SOURCE_VIDEO_FILE_PATH,
    bucket_name = configurations.S3_BUCKET_NAME,
    object_key = configurations.VIDEO_OBJECT_KEY
)

if path_in_s3 is not None:
    hand_tracker_instance = hand_tracker.HandTracker()
    # Cada key en este diccionario corresponde a un frame del video y contiene las coordenadas de los puntos clave de las manos detectadas en ese frame.

    # Este método se debe poder obtener desde API Gateway para mandar la información.
    hand_landmarks = hand_tracker_instance.get_hands_landmarks(
        duration_ms = configurations.ANALYSIS_DURATION_MS,
        bucket_name = configurations.S3_BUCKET_NAME,
        object_key = configurations.VIDEO_OBJECT_KEY
    )

    hand_tracker_visualization = HandTrackerVisualization()
    hand_tracker_visualization.visualize_hand_landmarks(
        hand_landmarks = hand_landmarks,
        original_video_path = configurations.SOURCE_VIDEO_FILE_PATH,
        output_video_path = configurations.OUTPUT_VIDEO_PATH
    )