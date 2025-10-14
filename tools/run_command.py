from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import time
import ktoolkits

server_dict = {
    #前端展示节点:后端实际的请求地址
    "tencent-node-1": "https://175.178.7.60/console/api/v1",
}

image_dict = [
    {
        "name":"registry.cn-hangzhou.aliyuncs.com/kservice/kigo-kali",
        "version":"0.1"
    }
]

class KtoolkitsTool(Tool):

    def _ensure_start_sandbox(self, image:str, version:str):
        """
        Ensure that the sandbox is started with the specified image and version.
        """
        sandbox = None
        sandbox= ktoolkits.Tool.get_current_sandbox()
        if sandbox is None:
            name = f"sandbox_default_name_{int(time.time())}"
            sandbox = ktoolkits.Tool.create_sandbox(name=name,
                                                    image=image,
                                                    version=version)
            if sandbox is None:
                return None
        else:
            sandbox.start()
        return sandbox
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        endpoint = self.runtime.credentials.get("server", None)
        apikey   = self.runtime.credentials.get("apikey", None)
        image    = self.runtime.credentials.get("image", None)
        version  = self.runtime.credentials.get("version", None)

        #set kito env info
        ktoolkits.base_http_api_url=endpoint
        ktoolkits.api_key = apikey

        command = tool_parameters.get("command",None)

        print(ktoolkits.version.__version__)

        task_output = ""

        try:
            sandbox = self._ensure_start_sandbox(image=image,version=version)

            if sandbox is not None:

                response = sandbox.process.exec(command=command,cwd="/workspace")

                if int(response.exit_code) == 0 :
                    task_output = response.result
                else:
                    task_output = "error: run command failed"

            else:
                task_output = "error: sandbox initial failed"

        except Exception as e:

            task_output =  f"error: run command error, {str(e)}"

        yield self.create_text_message(task_output)
