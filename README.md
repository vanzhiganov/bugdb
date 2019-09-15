# BugDB

## Features

- list of tasks for each team
- priority assigned and capability to change priority
- sort by priority
- listing of tasks:
    - user assigned
    - department logged
    - title
    - priority
- listing of a particular bug:
    - title
    - description
    - ability to update.

## Requirements

- Flask: https://palletsprojects.com/p/flask/
- Python 3.7
- PostgreSQL or MySQL server 5.3+

## Python Module requirements

- SQLAlchemy
- MySQLdb (http://sourceforge.net/projects/mysql-python/)
- Psycopg2 (https://github.com/psycopg/psycopg2)

## How to install and run

Connect to DB on mysql and create the schema using the file schema.sql:

```mysql --user=<MYSQLUSERNAME> -p -D >MYSQLDATABASENAME> < schema.sql```

You can make changes to schema.sql but only for the STATUSes in the insert statements.

First edit the db.py file to include your own mysql database, user and password. Currently its set to tasks/tasks12@tasksdb

Then run the below from a shell

`$ python tasks.py`


## TODO

Todo is a list of things I hope to add in the next release and does not really include the complete to-do list

1. Categories and subcategories of bugs.
2. Archive bugs.
3. Report to show how many bugs were logged, solved in the past one week, month.

# Database

    export FLASK_APP=BugDB/__init__.py
    
    flask db init -d BugDB/Models/migrations
    
    flask db revision --autogenerate -d BugDB/Models/migrations
    
    flask db upgrade -d BugDB/Models/migrations