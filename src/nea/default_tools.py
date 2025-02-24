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
import json
import re
from dataclasses import dataclass
from typing import Dict, Optional
from huggingface_hub import hf_hub_download, list_spaces

from transformers.utils import is_offline_mode
from transformers.models.whisper import (
    WhisperProcessor,
    WhisperForConditionalGeneration,
)

from .local_python_executor import (
    BASE_BUILTIN_MODULES,
    BASE_PYTHON_TOOLS,
    evaluate_python_code,
)
from .tools import TOOL_CONFIG_FILE, Tool, PipelineTool
from .types import AgentAudio


@dataclass
class PreTool:
    name: str
    inputs: Dict[str, str]
    output_type: type
    task: str
    description: str
    repo_id: str


def get_remote_tools(logger, organization="huggingface-tools"):
    if is_offline_mode():
        logger.info("You are in offline mode, so remote tools are not available.")
        return {}

    spaces = list_spaces(author=organization)
    tools = {}
    for space_info in spaces:
        repo_id = space_info.id
        resolved_config_file = hf_hub_download(
            repo_id, TOOL_CONFIG_FILE, repo_type="space"
        )
        with open(resolved_config_file, encoding="utf-8") as reader:
            config = json.load(reader)
        task = repo_id.split("/")[-1]
        tools[config["name"]] = PreTool(
            task=task,
            description=config["description"],
            repo_id=repo_id,
            name=task,
            inputs=config["inputs"],
            output_type=config["output_type"],
        )

    return tools


class PythonInterpreterTool(Tool):
    name = "python_interpreter"
    description = "This is a tool that evaluates python code. It can be used to perform calculations."
    inputs = {
        "code": {
            "type": "string",
            "description": "The python code to run in interpreter",
        }
    }
    output_type = "string"

    def __init__(self, *args, authorized_imports=None, **kwargs):
        if authorized_imports is None:
            self.authorized_imports = list(set(BASE_BUILTIN_MODULES))
        else:
            self.authorized_imports = list(
                set(BASE_BUILTIN_MODULES) | set(authorized_imports)
            )
        self.base_python_tools = BASE_PYTHON_TOOLS
        self.python_evaluator = evaluate_python_code
        super().__init__(*args, **kwargs)

    def forward(self, code: str) -> str:
        state = {}
        try:
            output = str(
                self.python_evaluator(
                    code,
                    state=state,
                    static_tools=self.base_python_tools,
                    authorized_imports=self.authorized_imports,
                )
            )
            return f"Stdout:\n{state['print_outputs']}\nOutput: {output}"
        except Exception as e:
            return f"Error: {str(e)}"


class FinalAnswerTool(Tool):
    name = "final_answer"
    description = "Provides a final answer to the given problem."
    inputs = {
        "answer": {"type": "any", "description": "The final answer to the problem"}
    }
    output_type = "any"

    def forward(self, answer):
        return answer


class UserInputTool(Tool):
    name = "user_input"
    description = "Asks for user's input on a specific question"
    inputs = {
        "question": {"type": "string", "description": "The question to ask the user"}
    }
    output_type = "string"

    def forward(self, question):
        user_input = input(f"{question} => ")
        return user_input


class DuckDuckGoSearchTool(Tool):
    name = "web_search"
    description = """Performs a duckduckgo web search based on your query (think a Google search) then returns the top search results as a list of dict elements.
    Each result has keys 'title', 'href' and 'body'."""
    inputs = {
        "query": {"type": "string", "description": "The search query to perform."}
    }
    output_type = "any"

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import time

def execute_code_action(
    code_action: str,
    language: str = "python",
    theme: str = "monokai",
    title: str = "Executing Code",
    show_execution_time: bool = True,
    log_file: str = None,
):
    """
    Displays a panel with the code to be executed and optionally logs the action.
    
    Args:
        code_action (str): The code to display and execute.
        language (str): The programming language for syntax highlighting. Default is 'python'.
        theme (str): The theme for syntax highlighting. Default is 'monokai'.
        title (str): The title of the panel. Default is 'Executing Code'.
        show_execution_time (bool): Whether to display execution time. Default is True.
        log_file (str): Path to a log file to save the displayed code. Default is None.
    """
    console = Console()
    
    # Highlight the code
    syntax_highlighted_code = Syntax(
        code_action,
        lexer=language,
        theme=theme,
        word_wrap=True,
        line_numbers=True,
    )

    # Create a panel to wrap the syntax-highlighted code
    code_panel = Panel(
        syntax_highlighted_code,
        title=f"[bold]{title}:",
        title_align="left",
        border_style="cyan",
    )

    # Print the panel to the console
    console.print(code_panel)

    # Optionally log the code to a file
    if log_file:
        try:
            with open(log_file, "a") as file:
                file.write(f"{'-'*40}\n{time.ctime()}\n")
                file.write(code_action + "\n")
                console.log(f"Code logged to {log_file}")
        except Exception as e:
            console.print(f"[red]Failed to log code: {str(e)}")

    # Measure execution time (if enabled)
    if show_execution_time:
        start_time = time.time()
        console.print("\n[bold cyan]Execution started...[/bold cyan]")
        # Simulate execution (replace with actual execution logic if needed)
        time.sleep(1)  # Placeholder for actual execution
        end_time = time.time()
       

    def forward(self, query: str) -> str:
        results = self.ddgs.text(query, max_results=10)
        postprocessed_results = [
            f"[{result['title']}]({result['href']})\n{result['body']}"
            for result in results
        ]
        return "## Search Results\n\n" + "\n\n".join(postprocessed_results)


class GoogleSearchTool(Tool):
    name = "web_search"
    description = """Performs a google web search for your query then returns a string of the top search results."""
    inputs = {
        "query": {"type": "string", "description": "The search query to perform."},
        "filter_year": {
            "type": "integer",
            "description": "Optionally restrict results to a certain year",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self):
        super().__init__(self)
        import os

        self.serpapi_key = os.getenv("SERPAPI_API_KEY")

    def forward(self, query: str, filter_year: Optional[int] = None) -> str:
        import requests

        if self.serpapi_key is None:
            raise ValueError(
                "Missing SerpAPI key. Make sure you have 'SERPAPI_API_KEY' in your env variables."
            )

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.serpapi_key,
            "google_domain": "google.com",
        }
        if filter_year is not None:
            params["tbs"] = (
                f"cdr:1,cd_min:01/01/{filter_year},cd_max:12/31/{filter_year}"
            )

import requests

def fetch_results(query, params, filter_year=None):
    response = requests.get("https://serpapi.com/search.json", params=params)

    # Handle response status
    if response.status_code != 200:
        raise ValueError(response.json())

    results = response.json()

    # Check for 'organic_results' key
    if "organic_results" not in results:
        year_filter_message = f" with filtering on year={filter_year}" if filter_year else ""
        raise Exception(
            f"'organic_results' key not found for query: '{query}'{year_filter_message}. "
            f"Use a less restrictive query or adjust/remove the year filter."
        )

    # Check for empty 'organic_results'
    if not results["organic_results"]:
        year_filter_message = f" with filter year={filter_year}" if filter_year else ""
        return f"No results found for '{query}'{year_filter_message}. Try with a more general query or remove the year filter."

    return results
    
        web_snippets = []
        if "organic_results" in results:
            for idx, page in enumerate(results["organic_results"]):
                date_published = ""
                if "date" in page:
                    date_published = "\nDate published: " + page["date"]

                source = ""
                if "source" in page:
                    source = "\nSource: " + page["source"]

                snippet = ""
                if "snippet" in page:
                    snippet = "\n" + page["snippet"]

                redacted_version = f"{idx}. [{page['title']}]({page['link']}){date_published}{source}\n{snippet}"

                redacted_version = redacted_version.replace(
                    "Your browser can't play this video.", ""
                )
                web_snippets.append(redacted_version)

        return "## Search Results\n" + "\n\n".join(web_snippets)


class VisitWebpageTool(Tool):
    name = "visit_webpage"
    description = "Visits a webpage at the given url and reads its content as a markdown string. Use this to browse webpages."
    inputs = {
        "url": {
            "type": "string",
            "description": "The url of the webpage to visit.",
        }
    }
    output_type = "string"

    def forward(self, url: str) -> str:
        try:
            from markdownify import markdownify
            import requests
            from requests.exceptions import RequestException
        except ImportError:
            raise ImportError(
                "You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests`."
            )
        try:
            # Send a GET request to the URL
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Convert the HTML content to Markdown
            markdown_content = markdownify(response.text).strip()

            # Remove multiple line breaks
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

            return markdown_content

        except RequestException as e:
            return f"Error fetching the webpage: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"


class SpeechToTextTool(PipelineTool):
    default_checkpoint = "openai/whisper-large-v3-turbo"
    description = "This is a tool that transcribes an audio into text. It returns the transcribed text."
    name = "transcriber"
    pre_processor_class = WhisperProcessor
    model_class = WhisperForConditionalGeneration

    inputs = {
        "audio": {
            "type": "audio",
            "description": "The audio to transcribe. Can be a local path, an url, or a tensor.",
        }
    }
    output_type = "string"

    def encode(self, audio):
        audio = AgentAudio(audio).to_raw()
        return self.pre_processor(audio, return_tensors="pt")

    def forward(self, inputs):
        return self.model.generate(inputs["input_features"])

    def decode(self, outputs):
        return self.pre_processor.batch_decode(outputs, skip_special_tokens=True)[0]


__all__ = [
    "PythonInterpreterTool",
    "FinalAnswerTool",
    "UserInputTool",
    "DuckDuckGoSearchTool",
    "GoogleSearchTool",
    "VisitWebpageTool",
    "SpeechToTextTool",
]
