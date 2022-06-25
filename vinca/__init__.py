from vinca._config import dolt_repo

def run():
    if dolt_repo and dolt_repo.days_since_last_sync > 1:
            dolt_repo.ask_and_merge()

    try:
        from fire import Fire
        from vinca import _cli_objects
        Fire(component=_cli_objects, name='vinca')
    finally:
        if dolt_repo:
            dolt_repo.commit()

    

