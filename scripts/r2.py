import boto3
from mypy_boto3_s3 import S3Client
from pydantic_settings import BaseSettings, SettingsConfigDict

class AWSSettings(BaseSettings):
    access_key_id: str
    bucket_name: str
    endpoint_url: str
    secret_access_key: str
    region_name: str = "auto"

    model_config = SettingsConfigDict(
        env_prefix="AWS_",
        extra="ignore",
    )

def get_r2_client(settings: AWSSettings | None = None) -> S3Client:
    cfg = settings or AWSSettings()
    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint_url,
        aws_access_key_id=cfg.access_key_id,
        aws_secret_access_key=cfg.secret_access_key,
        region_name=cfg.region_name,
    )