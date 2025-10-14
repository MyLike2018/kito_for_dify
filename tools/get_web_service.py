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
        image    = self.runtime.credentials.get("image", None)
        version  = self.runtime.credentials.get("version", None)

        #set kito env info
        ktoolkits.base_http_api_url=endpoint
        ktoolkits.api_key = apikey
        
        print(ktoolkits.version.__version__)

        print(image)

        task_output = ""

        try:
            sandbox = self._ensure_start_sandbox(image=image,version=version)

            base_url = sandbox.get_web_service()

            task_output = base_url

        except Exception as e:
            
            task_output= f"error: get web service error, {str(e)}"

        yield self.create_text_message(task_output)
