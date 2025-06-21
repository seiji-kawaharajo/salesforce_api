import json
from typing import Any

from pydantic import BaseModel, Field, SecretStr, ValidationError
from simple_salesforce.api import Salesforce


class SalesforceConnectionSettings(BaseModel):
    username: str
    password: SecretStr
    security_token: SecretStr
    domain: str = Field(
        "login",
        description="Salesforce domain (e.g., 'login', 'test', 'csXX.salesforce.com')",
    )
    api_version: str = Field(
        "64.0",
        description="Salesforce API Version",
    )


class Sf(Salesforce):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    @classmethod
    def from_env(
        cls,
        json_str: str,
    ) -> "Sf":
        if not isinstance(json_str, str) or not json_str.strip():
            raise ValueError("有効なJSON文字列が提供されていません。")
        try:
            _raw_config: dict[str, Any] = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"提供されたJSON文字列の形式が不正です: {e}") from e

        try:
            parsed_settings = SalesforceConnectionSettings.model_validate(_raw_config)
        except ValidationError as e:
            raise ValueError(
                f"Salesforce設定のバリデーションに失敗しました: {e}"
            ) from e
        except Exception as e:
            raise ValueError(f"設定パース中に予期せぬエラーが発生しました: {e}") from e

        return cls(
            username=parsed_settings.username,
            password=parsed_settings.password.get_secret_value(),
            security_token=parsed_settings.security_token.get_secret_value(),
            domain=parsed_settings.domain,
            version=parsed_settings.api_version,
        )
