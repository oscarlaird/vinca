# Move everything in _cli_objects into the module namespace
# Python Fire will give us access to everything in the module's namespace
from vinca import _cli_objects
for name, obj in vars(_cli_objects).items():
        if name.startswith('_'):
                continue
        globals()[name] = obj
del name, obj
