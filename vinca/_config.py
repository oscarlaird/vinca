# location of the database file
collection_path = '~/cards.db'

# cards with hidden_tags can only be accessed using `vinca -a ...`
# the option flag -a stands for "all cards"
hidden_tags = ['private',]

# integrate vinca with dolthub for easy database backup across multiple devices
# if this is None we will use the "collection_path" variable instead
dolt_repo_path = None




















# DO NOT EDIT
# ----------------------------------------------

if dolt_repo_path:
        from vinca import _dolt
dolt_repo = None if not dolt_repo_path else _dolt.Dolt_Repo(dolt_repo_path)
