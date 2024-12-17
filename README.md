

# Setup

Install PyQt using brew. Currently this will instal PyQt 6. Presumability this might change in the future when newer versions are released.

```sh
brew install pyqt
```

Create the virtual environment from the root of the repo.

```sh
./scripts/createEnv.sh
```

# Env file

Put an env file in the root of the repo with the following entries.

```
HARVEST_ACCESS_TOKEN=XXXXXXXXX
HARVEST_ACCOUNT_ID=XXXXXXXXXX
```

# Alfred Script

The following is needed at the start of an Alfred workflow to include the env file in the command to launch the software.

```bash
export $(grep -v '^#' PATH_HERE/.env | xargs) && PATH_HERE/.venv/bin/python3 PATH_HERE/src/MainWindow.py
```

# Resources

- [Python Module Importing Tutorial](https://towardsdatascience.com/understanding-python-imports-init-py-and-pythonpath-once-and-for-all-4c5249ab6355)
- [MUI Icons](https://materialui.co/icon/calendar-today)