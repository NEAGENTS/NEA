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

__version__ = "1.1.0.dev0"

from typing import TYPE_CHECKING
from transformers.utils import _LazyModule
from transformers.utils.import_utils import define_import_structure

if TYPE_CHECKING:
    # Import all modules directly during type checking or IDE code introspection.
    from .agents import *
    from .default_tools import *
    from .gradio_ui import *
    from .models import *
    from .local_python_executor import *
    from .e2b_executor import *
    from .monitoring import *
    from .prompts import *
    from .tools import *
    from .types import *
    from .utils import *

else:
    # Lazy loading for runtime performance optimization.
    import sys
    _file = globals().get("__file__", None)
    import_structure = define_import_structure(_file)

    # Add the version key explicitly to the import structure.
    import_structure[""] = {"__version__": __version__}

    # Assign the `_LazyModule` instance to this module's namespace.
    sys.modules[__name__] = _LazyModule(
        __name__,
        _file,
        import_structure,
        module_spec=__spec__,
        extra_objects={"__version__": __version__},
    )
