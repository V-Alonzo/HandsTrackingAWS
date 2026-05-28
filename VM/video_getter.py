import os
import tempfile
from typing import Generator, Optional

import boto3
import cv2
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

import VM.configurations as configurations


class S3VideoGetter:
	def __init__(
		self,
		bucket_name: str,
		object_key: str,
		aws_region: Optional[str] = None,
	) -> None:
		self.bucket_name = bucket_name
		self.object_key = object_key
		self.aws_region = aws_region
		self.s3_client = boto3.client("s3", region_name=aws_region)
		self._temp_file_path: Optional[str] = None
		self._capture: Optional[cv2.VideoCapture] = None

	@classmethod
	def from_s3_uri(cls, s3_uri: str, aws_region: Optional[str] = None) -> "S3VideoGetter":
		if not s3_uri.startswith("s3://"):
			raise ValueError("La ruta debe comenzar con 's3://'.")

		bucket_and_key = s3_uri[5:]
		if "/" not in bucket_and_key:
			raise ValueError("La ruta S3 debe incluir bucket y object key.")

		bucket_name, object_key = bucket_and_key.split("/", 1)
		return cls(bucket_name=bucket_name, object_key=object_key, aws_region=aws_region)

	def open(self) -> None:
		if self._capture is not None and self._capture.isOpened():
			return

		self._temp_file_path = self._download_video_to_temp_file()
		self._capture = cv2.VideoCapture(self._temp_file_path)

		if not self._capture.isOpened():
			self.close()
			raise RuntimeError(
				f"No se pudo abrir el video descargado desde s3://{self.bucket_name}/{self.object_key}"
			)

	def read_frame(self):
		if self._capture is None:
			self.open()

		if self._capture is None:
			return False, None

		return self._capture.read()

	def current_timestamp_ms(self) -> float:
		if self._capture is None:
			self.open()

		if self._capture is None:
			return 0.0

		return float(self._capture.get(cv2.CAP_PROP_POS_MSEC))

	def frames(self) -> Generator:
		while True:
			ok, frame = self.read_frame()
			if not ok:
				break
			yield frame

	def close(self) -> None:
		if self._capture is not None:
			self._capture.release()
			self._capture = None

		if self._temp_file_path and os.path.exists(self._temp_file_path):
			os.remove(self._temp_file_path)
			self._temp_file_path = None

	def _download_video_to_temp_file(self) -> str:
		file_descriptor, temp_file_path = tempfile.mkstemp(suffix=".mp4")
		os.close(file_descriptor)

		try:
			self.s3_client.download_file(self.bucket_name, self.object_key, temp_file_path)
			return temp_file_path
		except NoCredentialsError as error:
			os.remove(temp_file_path)
			raise RuntimeError("No se encontraron credenciales de AWS.") from error
		except (ClientError, BotoCoreError) as error:
			os.remove(temp_file_path)
			raise RuntimeError(
				f"No se pudo descargar s3://{self.bucket_name}/{self.object_key}"
			) from error

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, exc_type, exc_value, traceback) -> None:
		self.close()


def build_default_video_getter(bucket_name: str, object_key: str) -> S3VideoGetter:
	return S3VideoGetter(
		bucket_name=bucket_name,
		object_key=object_key,
	)
