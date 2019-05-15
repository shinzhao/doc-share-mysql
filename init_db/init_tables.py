"""
This file file contains all the queries for creating tables
To initialize database, please run 'run.py'
"""
def init(mycursor):
    # Create Users table
    mycursor.execute(
        """CREATE TABLE Users(
            id        INT AUTO_INCREMENT PRIMARY KEY,
            user_type VARCHAR(10),
            username  VARCHAR(20),
            password  VARCHAR(20) NOT NULL,
            email     VARCHAR(20),
            firstName VARCHAR(20),
            lastName  VARCHAR(20)
        );"""
    )
    # Add temp users
    mycursor.execute("INSERT INTO Users(user_type, username, password) VALUES ('admin', 'xin', 'xin');")
    mycursor.execute("INSERT INTO Users(user_type, username, password) VALUES ('user', 'shin', 'shin');")


    # Create BlackList table
    mycursor.execute(
        """CREATE TABLE BlackList(
            id        INT PRIMARY KEY,
            username  VARCHAR(20)
        );"""
    )

    # Create Documents table
    mycursor.execute(
        """CREATE TABLE Documents(
            status      VARCHAR(10),
            id          INT AUTO_INCREMENT PRIMARY KEY,
            title       VARCHAR(100) NOT NULL,
            owner       VARCHAR(20) NOT NULL,
            content     TEXT,
            create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            modify_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );"""
    )
    # Add temp docs
    mycursor.execute("INSERT INTO Documents(status, title, owner, content) VALUES ('private', 'xin1', 'xin', 'test');")
    mycursor.execute("INSERT INTO Documents(status, title, owner, content) VALUES ('private', 'xin2', 'xin', 'test');")
    mycursor.execute("INSERT INTO Documents(status, title, owner, content) VALUES ('private', 'shin1', 'shin', 'test');")
    mycursor.execute("INSERT INTO Documents(status, title, owner, content) VALUES ('private', 'shin2', 'shin', 'test');")
    mycursor.execute("INSERT INTO Documents(status, title, owner, content) VALUES ('public', 'noone1', 'noone', 'test');")


    # Create History table
    mycursor.execute(
        """CREATE TABLE History(
            record_id   INT AUTO_INCREMENT PRIMARY KEY,
            doc_id      INT,
            title       VARCHAR(100) NOT NULL,
            user        VARCHAR(20) NOT NULL,
            content     TEXT,
            modify_date TIMESTAMP
        );"""
    )