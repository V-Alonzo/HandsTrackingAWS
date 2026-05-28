import Local.video_uploader as video_uploader

from Local.hand_tracker_visualization import HandTrackerVisualization

import Local.configurations as configurations

import requests
import os
import json

from mediapipe.framework.formats import landmark_pb2

import dotenv
dotenv.load_dotenv("Local/secret/.env")


def deserialize_hand_landmarks(serialized_hand_landmarks: dict) -> dict:
    hand_landmarks = {}

    for timestamp_ms, hands in serialized_hand_landmarks.items():
        hand_landmarks[int(timestamp_ms)] = [
            landmark_pb2.NormalizedLandmarkList(
                landmark=[
                    landmark_pb2.NormalizedLandmark(
                        x=landmark["x"],
                        y=landmark["y"],
                        z=landmark["z"],
                    )
                    for landmark in hand
                ]
            )
            for hand in hands
        ]

    return hand_landmarks

path_in_s3 = video_uploader.upload_video_to_s3(
    file_path = configurations.SOURCE_VIDEO_FILE_PATH,
    bucket_name = configurations.S3_BUCKET_NAME,
    object_key = configurations.VIDEO_OBJECT_KEY
)

if path_in_s3 is not None:
    payload = {
        "duration_ms": configurations.ANALYSIS_DURATION_MS,
        "bucket_name": configurations.S3_BUCKET_NAME,
        "object_key": configurations.VIDEO_OBJECT_KEY
    }

    response = requests.get(f"{os.getenv('BASE_URL_EC2')}/get_hand_landmarks", params=payload)
    response.raise_for_status()

    response = response.json()

    with open(configurations.OUTPUT_HAND_LANDMARKS_JSON_PATH, "w") as f:
        json.dump(response["hand_landmarks"], f)

    hand_landmarks = deserialize_hand_landmarks(response["hand_landmarks"])

    hand_tracker_visualization = HandTrackerVisualization()
    hand_tracker_visualization.visualize_hand_landmarks(
        hand_landmarks = hand_landmarks,
        original_video_path = configurations.SOURCE_VIDEO_FILE_PATH,
        output_video_path = configurations.OUTPUT_VIDEO_PATH
    )