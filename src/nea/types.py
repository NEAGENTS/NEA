# coding=utf-8
# Copyright 2024 HuggingFace Inc.

import os
import pathlib
import tempfile
import uuid
from io import BytesIO
import numpy as np
import logging

from transformers.utils import (
    is_soundfile_availble,
    is_torch_available,
    is_vision_available,
)

if is_vision_available():
    from PIL import Image
    from PIL.Image import Image as ImageType
else:
    ImageType = object

if is_torch_available():
    import torch
    from torch import Tensor
else:
    Tensor = object

if is_soundfile_availble():
    import soundfile as sf

logger = logging.getLogger(__name__)


class AgentType:
    """
    Abstract base class for agent types (text, image, audio).
    Behaves as the intended type while providing stringification
    and notebook-friendly display functionality.
    """

    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self.to_string()

    def to_raw(self):
        logger.error(
            "This is a raw AgentType of unknown type. Display and string conversion may be unreliable."
        )
        return self._value

    def to_string(self):
        logger.error(
            "This is a raw AgentType of unknown type. Display and string conversion may be unreliable."
        )
        return str(self._value)


class AgentText(AgentType):
    """
    Text type for agents. Behaves as a string.
    """

    def __init__(self, value: str):
        if not isinstance(value, str):
            raise TypeError("AgentText must be initialized with a string.")
        super().__init__(value)

    def to_raw(self):
        return self._value

    def to_string(self):
        return self._value

    def upper(self):
        return AgentText(self._value.upper())

    def lower(self):
        return AgentText(self._value.lower())

    def split(self, sep=None):
        return self._value.split(sep)

    def __repr__(self):
        return f"AgentText({repr(self._value)})"

    def __eq__(self, other):
        if isinstance(other, AgentText):
            return self._value == other._value
        if isinstance(other, str):
            return self._value == other
        return NotImplemented


class AgentImage(AgentType):
    """
    Image type for agents. Behaves as a PIL.Image.
    """

    def __init__(self, value):
        super().__init__(value)

        if not is_vision_available():
            raise ImportError("Pillow must be installed to handle images.")

        self._path = None
        self._raw = None
        self._tensor = None

        if isinstance(value, AgentImage):
            self._raw, self._path, self._tensor = value._raw, value._path, value._tensor
        elif isinstance(value, ImageType):
            self._raw = value
        elif isinstance(value, bytes):
            self._raw = Image.open(BytesIO(value))
        elif isinstance(value, (str, pathlib.Path)):
            self._path = value
        elif is_torch_available() and isinstance(value, torch.Tensor):
            self._tensor = value
        else:
            raise TypeError(f"Unsupported type for AgentImage: {type(value)}")

    def to_raw(self):
        if self._raw:
            return self._raw

        if self._path:
            self._raw = Image.open(self._path)
            return self._raw

        if self._tensor is not None:
            array = self._tensor.cpu().detach().numpy()
            self._raw = Image.fromarray((255 - array * 255).astype(np.uint8))
            return self._raw

        raise ValueError("Unable to convert to raw image format.")

    def to_string(self):
        if self._path:
            return self._path

        if self._raw:
            with tempfile.TemporaryDirectory() as temp_dir:
                self._path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
                self._raw.save(self._path, format="PNG")
                return self._path

        raise ValueError("Unable to convert to string representation.")

    def save_tensor_as_image(self):
        if self._tensor is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.png")
                array = self._tensor.cpu().detach().numpy()
                img = Image.fromarray((255 - array * 255).astype(np.uint8))
                img.save(file_path, format="PNG")
                return file_path
        raise ValueError("No tensor data to save as image.")


class AgentAudio(AgentType):
    """
    Audio type for agents. Behaves as a torch.Tensor.
    """

    def __init__(self, value, samplerate=16000):
        super().__init__(value)

        if not is_soundfile_availble():
            raise ImportError("SoundFile must be installed to handle audio.")

        self._path = None
        self._tensor = None
        self.samplerate = samplerate

        if isinstance(value, (str, pathlib.Path)):
            self._path = value
        elif is_torch_available() and isinstance(value, torch.Tensor):
            self._tensor = value
        elif isinstance(value, tuple) and len(value) == 2:
            self.samplerate, tensor_data = value
            self._tensor = (
                torch.from_numpy(tensor_data)
                if isinstance(tensor_data, np.ndarray)
                else torch.tensor(tensor_data)
            )
        else:
            raise ValueError(f"Unsupported audio type: {type(value)}")

    def to_raw(self):
        if self._tensor is not None:
            return self._tensor

        if self._path:
            if "://" in str(self._path):  # Handle remote URLs
                response = requests.get(self._path)
                response.raise_for_status()
                tensor, self.samplerate = sf.read(BytesIO(response.content))
            else:  # Handle local file paths
                tensor, self.samplerate = sf.read(self._path)
            self._tensor = torch.tensor(tensor)
            return self._tensor

        raise ValueError("Unable to convert to raw audio format.")

    def to_string(self):
        if self._path:
            return self._path

        if self._tensor is not None:
            with tempfile.TemporaryDirectory() as temp_dir:
                self._path = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")
                sf.write(self._path, self._tensor.numpy(), samplerate=self.samplerate)
                return self._path

        raise ValueError("Unable to convert to string representation.")


AGENT_TYPE_MAPPING = {"string": AgentText, "image": AgentImage, "audio": AgentAudio}
INSTANCE_TYPE_MAPPING = {
    str: AgentText,
    ImageType: AgentImage,
    torch.Tensor: AgentAudio if is_torch_available() else None,
}


def handle_agent_input_types(*args, **kwargs):
    args = [arg.to_raw() if isinstance(arg, AgentType) else arg for arg in args]
    kwargs = {
        k: (v.to_raw() if isinstance(v, AgentType) else v) for k, v in kwargs.items()
    }
    return args, kwargs


def handle_agent_output_types(output, output_type=None):
    if output_type in AGENT_TYPE_MAPPING:
        return AGENT_TYPE_MAPPING[output_type](output)
    for _k, _v in INSTANCE_TYPE_MAPPING.items():
        if isinstance(output, _k):
            return _v(output)
    return output


__all__ = ["AgentType", "AgentImage", "AgentText", "AgentAudio"]
