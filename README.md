

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

# Build

The pip module called `pyinstaller` is used to build a deployment package. See the build scripts in the root `scripts` folder. pyinstaller bundles all the files necessary to run the application into an executable. The windows version uses the `--onefile` parameter to combine everything into a single executable. Without this there's an `_internal` folder placed next to the executable that needs to be shipped with the executable. The steps to use pyinstaller were learned [here](https://www.pythonguis.com/tutorials/packaging-pyqt5-pyside2-applications-windows-pyinstaller/).

A Windows build must be generated on a Windows machine (duh).

# Deployment

The built executable can be zipped or put directly on GitHub as part of a [release](https://github.com/Riverscapes/py-champ-workbench/releases). 

# Running the Deployed Application

On Windows, simply double clicked the deployed executable. A login screen prompting for credentials will appear. You can use this screen or alternatively you can place an `.env` file next to the executable with the following items:

```sh
DB_HOST=XXXXXXXXXXXXX
DB_PORT=XXXXXXXXXXXXX
DB_NAME=XXXXXXXXXXXXX
DB_USER=XXXXXXXXXXXXX
DB_PASSWORD=XXXXXXXXXXXXX
SSLROOTCERT=XXXXXXXXXXXXX
SSLCLIENTCERT=XXXXXXXXXXXXX
SSLKEY=XXXXXXXXXXXXX
```