"""
Run this script to initialize a database for doc-share
PLEASE CHANGE CONFIG TO YOUR OWN SETTING
"""
import mysql.connector
import init_tables

# Configuration
# Please change config below 
config = {
    'user': "root",
    'password': "root",
    'host': "127.0.0.1",
    'port': "3306"
}
db_name = "docshare"

def main():
    # Connect to db server
    mydb = mysql.connector.connect(**config)
    mycursor = mydb.cursor()

    # Create a new db
    mycursor.execute("DROP DATABASE IF EXISTS %s" % db_name)
    mycursor.execute("CREATE DATABASE %s" % db_name)
    mycursor.execute("USE %s" % db_name)

    # Create tables
    init_tables.init(mycursor)
    mydb.commit()

if __name__ == '__main__':
    main()
