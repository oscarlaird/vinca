def run():
    from fire import Fire
    from vinca import _cli_objects
    Fire(component=_cli_objects, name='vinca')
