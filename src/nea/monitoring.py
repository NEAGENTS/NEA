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
from .utils import console
from rich.text import Text


class Monitor:
    def __init__(self, tracked_model):
        self.step_durations = []
        self.tracked_model = tracked_model
        if (
            getattr(self.tracked_model, "last_input_token_count", "Not found")
            != "Not found"
        ):
            self.total_input_token_count = 0
            self.total_output_token_count = 0

    def get_total_token_counts(self):
        return {
            "input": self.total_input_token_count,
            "output": self.total_output_token_count,
        }

    def reset(self):
        self.step_durations = []
        self.total_input_token_count = 0
        self.total_output_token_count = 0

    def update_metrics(self, step_log):
        step_duration = step_log.duration
        self.step_durations.append(step_duration)
        console_outputs = (
            f"[Step {len(self.step_durations)-1}: Duration {step_duration:.2f} seconds"
        )

def update_token_counts(self, console):
    # Check if the tracked model has token count attributes
    last_input_token_count = getattr(self.tracked_model, "last_input_token_count", 0)
    last_output_token_count = getattr(self.tracked_model, "last_output_token_count", 0)

    # Only update counts if both token counts are non-zero
    if last_input_token_count or last_output_token_count:
        self.total_input_token_count += last_input_token_count
        self.total_output_token_count += last_output_token_count

        # Create the token count string in a readable format
        token_message = f"| Input tokens: {self.total_input_token_count:,} | Output tokens: {self.total_output_token_count:,} |"
    else:
        token_message = ""

    # Display the message with the token counts
    console.print(Text(f"{token_message}]", style="dim"))
