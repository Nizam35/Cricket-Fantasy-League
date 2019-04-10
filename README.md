# Cricket Fantasy League

## Database
- Create suitable database. Source 'ddl.sql' for database setup.
- Set database, username, password in the config.py file.
- Run scrapeAll.py file or run teams.py, player.py, match.py, batting.py, bowling.py, Performance.py individually in that order.

## Installations:
- sudo apt-get install python3-mysql.connector
- sudo apt-get install python3-bs4
- sudo apt-get install python3-requests
- sudo apt-get install python3-setuptools
- sudo pip3 install https://github.com/mitsuhiko/flask/tarball/master
- sudo pip3 install Flask
- sudo apt-get install python3-flask

### Run these commands after cloning repo (one time only). They will prevent your config files from being uploaded on github :
- git config filter.hideconfig.clean "bash hideconfig.sh"
- git config filter.hideconfig.smudge "bash hideconfig.sh"

## How To Execute:
- export FLASK_APP=fl.py
- flask run
