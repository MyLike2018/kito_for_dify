import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class YXITSECProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            server = credentials.get("server")
            apikey = credentials.get("apikey")
            if not apikey:
                raise ToolProviderCredentialValidationError("apikey is required")
            if not server:
                raise ToolProviderCredentialValidationError("server is required")

            #获取节点服务地址
            base_url = server.split("/console")[0]
            validate_url = f"{base_url}/validate_apikey?apikey={apikey}"
            resp = requests.get(validate_url, timeout=300, verify=False)

            if resp.status_code != 200:
                raise ToolProviderCredentialValidationError(f"Invalid response from validation server: {resp.status_code}")

            resp_json = resp.json()
            if resp_json.get("code") != 0:
                raise ToolProviderCredentialValidationError(f"Invalid API key: {resp_json.get('message')}")
        
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))