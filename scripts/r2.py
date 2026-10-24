import boto3
from mypy_boto3_s3 import S3Client
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class AWSSettings(BaseSettings):
    access_key_id: str = Field(default=...)
    bucket_name: str = Field(default=...)
    endpoint_url: str = Field(default=...)
    secret_access_key: str = Field(default=...)
    region_name: str = "auto"

    model_config = SettingsConfigDict(
        env_prefix="AWS_",
        extra="ignore",
    )

class R2Client:
    def __init__(self, settings: AWSSettings | None = None):
        self.settings = settings or AWSSettings()
        self.client: S3Client = boto3.client( # pyright: ignore[reportUnknownMemberType]
            "s3",
            endpoint_url=self.settings.endpoint_url,
            aws_access_key_id=self.settings.access_key_id,
            aws_secret_access_key=self.settings.secret_access_key,
            region_name=self.settings.region_name,
        )