import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import time
import ktoolkits
#ktoolkits.debug = True

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
                raise Exception("Kito create sandbox failed")
        else:
            sandbox.start()
        return sandbox


    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        endpoint = self.runtime.credentials.get("server", None)
        apikey   = self.runtime.credentials.get("apikey", None)
        #获取对应的value值，不需要单独处理
        image    = self.runtime.credentials.get("image", None)
        version  = self.runtime.credentials.get("version", None)

        #set kito env info
        ktoolkits.base_http_api_url=endpoint
        ktoolkits.api_key = apikey
        
        print(ktoolkits.version.__version__)

        task_output = ""

        try:
            sandbox = self._ensure_start_sandbox(image=image,version=version)

            #mcp config file path: /workspace/.mcp_server/config.json or /app/.mcp_server/config.json,but only one exists
            mcp_config_file=""
            
            if image.find("kigo-kali-image")>=0:
                mcp_config_file="/app/.mcp_server/config.json"
            
            else:
                mcp_config_file="/app/.mcp_server/config.json"

            command = f"cat {mcp_config_file}"
            response = sandbox.process.exec(command=command)

            mcpconfig = json.loads(response.result)
            top_level_keys = list(mcpconfig["mcpServers"].keys())

            base_url = sandbox.get_mcp_service()

            mcp_list = []
            for item in top_level_keys:
                mcp_service = base_url + f"servers/{item}/sse"
                mcp_list.append(mcp_service)

            task_output = "\n".join(mcp_list)

        except Exception as e:
            task_output= f"error: get mcp service error, {str(e)}"

        yield self.create_text_message(task_output)
