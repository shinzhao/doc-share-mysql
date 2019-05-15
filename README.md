# DocShare

## Requirements
- [Python3](https://www.python.org/downloads/)
- [MariaDB](https://mariadb.org/)
- [Flask](http://flask.pocoo.org/)
- [Mysql Connector for Python](https://dev.mysql.com/downloads/connector/python/)

## Initialize database
Go to folder **init_db**, open **run.py**.
Edit dictionary **config** to your database setting.
Then run following command to initialize the database.
```
python run.py
```

## Start server
Go back to main directory and run the following command.
Port 8000 is being used.
```
python app.py
```

## Open app
Open your web broswer and go to [127.0.0.1:8000](127.0.0.1:8000) to use the app.