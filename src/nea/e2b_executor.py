#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dotenv import load_dotenv
import textwrap
import base64
import pickle
from io import BytesIO
from PIL import Image

from e2b_code_interpreter import Sandbox
from typing import List, Tuple, Any
from .tool_validation import validate_tool_attributes
from .utils import instance_to_source, BASE_BUILTIN_MODULES, console
from .tools import Tool

load_dotenv()


class E2BExecutor:
    def __init__(self, additional_imports: List[str], tools: List[Tool]):
        self.custom_tools = {}
        self.sbx = Sandbox()  # "qywp2ctmu2q7jzprcf4j")
        # TODO: validate installing agents package or not
        # print("Installing agents package on remote executor...")
        # self.sbx.commands.run(
        #     "pip install git+https://github.com/huggingface/nea.git",
        #     timeout=300
        # )
        # print("Installation of agents package finished.")
        additional_imports = additional_imports + ["pickle5"]
        if len(additional_imports) > 0:
            execution = self.sbx.commands.run(
                "pip install " + " ".join(additional_imports)
            )
            if execution.error:
                raise Exception(f"Error installing dependencies: {execution.error}")
            else:
                console.print(f"Installation of {additional_imports} succeeded!")

            # Initialize a list to store the code for each tool
            tool_codes = []

            # Iterate through all the tools and generate their code representations
            for tool in tools:
                # Validate the tool's attributes (checking imports is skipped here)
                validate_tool_attributes(tool.__class__, check_imports=False)
                
                # Convert the tool instance to source code, ensuring it inherits from the Tool base class
                tool_code = instance_to_source(tool, base_cls=Tool)
                
                # Remove any unnecessary import statements, specifically Tool import
                tool_code = tool_code.replace("from nea.tools import Tool", "")
                
                # Append the tool initialization line to the code
                tool_code += f"\n# Initializing {tool.name} tool instance\n"
                tool_code += f"{tool.name} = {tool.__class__.__name__}()\n"
                
                # Add this tool's generated code to the list
                tool_codes.append(tool_code)

            # Generate the code for importing all the base built-in modules
            tool_definition_code = "\n".join(
                [f"import {module}" for module in BASE_BUILTIN_MODULES]
            )

            # Add a header or a description to clarify the following block
            tool_definition_code = (
                "# Importing the necessary built-in modules for tool definitions\n"
                + tool_definition_code
                + "\n"
            )

            # Optionally, you could add comments explaining the structure of the tool codes
            tool_definition_code += "\n# Now defining the tool instances with the generated code\n"

            # Join all the tool codes into a single string, with a separator between them
            final_code = "\n\n".join(tool_codes) + "\n"

            # Combine the module imports and tool definitions into one final output
            final_code = tool_definition_code + final_code

            # Optionally print or return the final generated code
            print(final_code)

            # Returning the final code can be used later
            return final_code

        tool_definition_code += textwrap.dedent("""
        class Tool:
            def __call__(self, *args, **kwargs):
                return self.forward(*args, **kwargs)

            def forward(self, *args, **kwargs):
                pass # to be implemented in child class
        """)
        tool_definition_code += "\n\n".join(tool_codes)

        tool_definition_execution = self.run_code_raise_errors(tool_definition_code)
        console.print(tool_definition_execution.logs)

    def run_code_raise_errors(self, code: str):
        execution = self.sbx.run_code(
            code,
        )
        if execution.error:
            execution_logs = "\n".join([str(log) for log in execution.logs.stdout])
            logs = execution_logs
            logs += "Executing code yielded an error:"
            logs += execution.error.name
            logs += execution.error.value
            logs += execution.error.traceback
            raise ValueError(logs)
        return execution

    def __call__(self, code_action: str, additional_args: dict) -> Tuple[Any, Any]:
        if len(additional_args) > 0:
            # Pickle additional_args to server
            import tempfile

            with tempfile.NamedTemporaryFile() as f:
                pickle.dump(additional_args, f)
                f.flush()
                with open(f.name, "rb") as file:
                    self.sbx.files.write("/home/state.pkl", file)
            remote_unloading_code = """import pickle
import os
print("File path", os.path.getsize('/home/state.pkl'))
with open('/home/state.pkl', 'rb') as f:
    pickle_dict = pickle.load(f)
locals().update({key: value for key, value in pickle_dict.items()})
"""
# Run the code and handle execution logs
execution = self.run_code_raise_errors(remote_unloading_code)

# Join logs in a single step and print them
console.print("\n".join(map(str, execution.logs.stdout)))

        execution = self.run_code_raise_errors(code_action)
        execution_logs = "\n".join([str(log) for log in execution.logs.stdout])
        if not execution.results:
            return None, execution_logs
        else:
            for result in execution.results:
                if result.is_main_result:
                    for attribute_name in ["jpeg", "png"]:
                        if getattr(result, attribute_name) is not None:
                            image_output = getattr(result, attribute_name)
                            decoded_bytes = base64.b64decode(
                                image_output.encode("utf-8")
                            )
                            return Image.open(BytesIO(decoded_bytes)), execution_logs
                    for attribute_name in [
                        "chart",
                        "data",
                        "html",
                        "javascript",
                        "json",
                        "latex",
                        "markdown",
                        "pdf",
                        "svg",
                        "text",
                    ]:
                        if getattr(result, attribute_name) is not None:
                            return getattr(result, attribute_name), execution_logs
            raise ValueError("No main result returned by executor!")


__all__ = ["E2BExecutor"]
