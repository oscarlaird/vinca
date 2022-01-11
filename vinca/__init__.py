from vinca import _cli_objects
for name, obj in vars(_cli_objects).items():
        if name.startswith('_'):
                continue
        globals()[name] = obj
del name, obj
