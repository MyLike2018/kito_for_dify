from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import time
import ktoolkits
#ktoolkits.debug = True

class KtoolkitsTool(Tool):

    def _ensure_start_sandbox(self, image:str, version:str):
        #image="registry.cn-hangzhou.aliyuncs.com/kservice/kigo-kali"
        #version="0.1"
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
        
        
        print(ktoolkits.version.__version__)

        task_output = ""

        try:
            sandbox = self._ensure_start_sandbox(image=image,version=version)

            if sandbox is not None:
                start_mcpserver = 'mcp-proxy --host 0.0.0.0 --port 8088 --path "/sandbox/webapp-${MCP_PORT}" --named-server-config /app/.mcp_server/config.json'
                response = sandbox.process.exec(command=start_mcpserver,cwd="/workspace",is_deamon=True)


                if int(response.exit_code) == 0:
                    task_output = f"success: start mcpserver {response.result}"
                else:
                    task_output  = f"error: start mcpserver failed,{response.result}"

            else:
                task_output = "error: sandbox initial failed"

        except Exception as e:
            task_output = f"error: start mcpserver error, {str(e)}"

        yield self.create_text_message(task_output)
