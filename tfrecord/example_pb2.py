# tfrecord/example_pb2.py
"""
A compatibility thin-wrapper that

1.  **Prefers TensorFlow’s own proto definitions** (they are already in the
    process’ address-space if the user imported TensorFlow / Keras /
    🤗 Transformers, and therefore cannot be re-declared).

2.  Falls back to the generated file that ships with *tfrecord* whenever
    TensorFlow is absent (e.g. in very light-weight, CPU-only environments).

It exports exactly the symbols that the original generated file contained,
so the rest of the *tfrecord* codebase — and your application code — do not
have to change at all.
"""

from types import ModuleType
import sys

# --------------------------------------------------------------------------- #
# ① Try TensorFlow’s own protos
# --------------------------------------------------------------------------- #
try:
    from tensorflow.core.example import example_pb2 as _ex_pb
    from tensorflow.core.example import feature_pb2 as _ft_pb      # holds Bytes/Int/Float lists
except Exception:  # TF not present (or very old)
    from tfrecord import _fallback_example_pb2 as _ex_pb
    _ft_pb = _ex_pb                    # the fallback already bundles every symbol

# --------------------------------------------------------------------------- #
# ② Build a synthetic module that contains **all** the names the rest of the
#    library expects, regardless of where they actually live.
# --------------------------------------------------------------------------- #
_mod = ModuleType(__name__)

for _name in (
    "BytesList", "FloatList", "Int64List",      # simple value wrappers
    "Feature", "Features",                      # individual feature + mapping
    "FeatureList", "FeatureLists",              # sequence-style feature containers
    "Example", "SequenceExample",               # top-level Example messages
):
    source = _ft_pb if hasattr(_ft_pb, _name) else _ex_pb
    setattr(_mod, _name, getattr(source, _name))

# the descriptor is occasionally accessed directly
_mod.DESCRIPTOR = _ex_pb.DESCRIPTOR

# Finally, register the synthetic module so that any subsequent
# `import tfrecord.example_pb2` (or the `from tfrecord import example_pb2`
# pattern that *tfrecord* uses internally) will receive this object.
sys.modules[__name__] = _mod
