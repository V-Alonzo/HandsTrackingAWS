from fastapi import Depends, FastAPI
from  VM.hand_tracker import HandTracker


app = FastAPI()

shared_hand_tracker = HandTracker()

def get_hand_tracker():
    return shared_hand_tracker


def serialize_hand_landmarks(hand_landmarks: dict) -> dict:
    serialized_hand_landmarks = {}

    for timestamp_ms, hands in hand_landmarks.items():
        serialized_hand_landmarks[str(int(round(timestamp_ms)))] = [
            [
                {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                }
                for landmark in hand.landmark
            ]
            for hand in hands
        ]

    return serialized_hand_landmarks

@app.get("/get_hand_landmarks")
def get_hand_landmarks(
    duration_ms: int,
    bucket_name: str,
    object_key: str,
    hand_tracker: HandTracker = Depends(get_hand_tracker),
):
    return {
        "hand_landmarks": serialize_hand_landmarks(
            hand_tracker.get_hands_landmarks(
                duration_ms=duration_ms,
                bucket_name=bucket_name,
                object_key=object_key,
            )
        )
    }