import os
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


def upload_video_to_s3(file_path: str, bucket_name: str, object_key: str) -> bool:
    """
    Sube un archivo de video local a un bucket de Amazon S3.

    Puedes verificar si el video se subió correctamente accediendo a la consola de AWS y ejecutar el comando:
    aws s3 ls s3://<bucket_name>/<object_key_without_filename>/

    :param file_path: Ruta local del archivo .mp4.
    :param bucket_name: Nombre del bucket de S3.
    :param object_key: Ruta/nombre que tendrá el archivo dentro de S3.
    :return: La ruta del archivo en S3 si se subió correctamente, None si falló.
    """

    if not os.path.isfile(file_path):
        print(f"El archivo no existe: {file_path}")
        return None

    if not file_path.lower().endswith(".mp4"):
        print("El archivo no parece ser un .mp4")
        return None

    s3_client = boto3.client("s3")

    try:
        s3_client.upload_file(
            Filename=file_path,
            Bucket=bucket_name,
            Key=object_key,
            ExtraArgs={
                "ContentType": "video/mp4"
            }
        )

        print("Video subido correctamente.")
        print(f"Ubicación: s3://{bucket_name}/{object_key}")
        return f"s3://{bucket_name}/{object_key}"

    except NoCredentialsError:
        print("No se encontraron credenciales de AWS.")
        print("Ejecuta: aws configure")
        return None

    except ClientError as error:
        print("Error al subir el archivo a S3:")
        print(error)
        return None
