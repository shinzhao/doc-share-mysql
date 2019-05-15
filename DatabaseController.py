import mysql.connector


class DatabaseController():

    # Initialize connection to database
    def __init__(self, config):
        self.mydb = mysql.connector.connect(**config)
        self.mycursor = self.mydb.cursor(dictionary=True)

    # Close connection to database
    def __del__(self):
        self.mydb.close()

    #####################
    #  User Management
    #####################

    # Sign up a new user to database
    def sign_up(self, username_in, password_in, email_in, firstName_in, lastName_in):
        qry = "SELECT username, password FROM Users WHERE username = %s;"
        self.mycursor.execute(qry, (username_in, ))
        try:
            user_info = self.mycursor.fetchone()
            print(f"DB: Username '{user_info['username']}' is taken")
            return False
        except:
            qry = "INSERT INTO Users VALUES (0, 'user', %s, %s, %s, %s, %s);"
            self.mycursor.execute(qry, (username_in, password_in, email_in, firstName_in, lastName_in))
            self.mydb.commit()
            return True

    # Log in
    def log_in(self, username_in, password_in):
        qry = "SELECT id, password FROM Users WHERE username = %s;"
        self.mycursor.execute(qry, (username_in, ))
        try:
            user_info = self.mycursor.fetchone()
            if password_in == user_info['password']:
                # Check if baned
                qry = "SELECT * FROM BlackList WHERE id=%s;"
                self.mycursor.execute(qry, (user_info['id'], ))
                is_in_blacklist = self.mycursor.fetchone()
                if is_in_blacklist:
                    print(f"DB: Login failed, account has been banned!")
                    return -1
                else:
                    print(f"DB: Login succeeds!")
                    return 1
            else:
                print(f"DB: Password doesn't match!")
                return 0
        except:
            print(f"DB: Username doesn't exist!")
            return 0

    # Get user type
    def get_user_type(self, username_in):
        qry = "SELECT user_type FROM Users WHERE username = %s;"
        self.mycursor.execute(qry, (username_in, ))
        user_type = self.mycursor.fetchone()  # Returns a dict
        user_type = user_type['user_type']  # Get a str
        return user_type

    # Get all users
    def get_all_users(self):
        qry = "SELECT * FROM Users;"
        self.mycursor.execute(qry)
        users = self.mycursor.fetchall()
        for user in users:
            qry = "SELECT * FROM BlackList WHERE id=%s;"
            self.mycursor.execute(qry, (user['id'], ))
        
            is_in_blacklist = self.mycursor.fetchone()
            if is_in_blacklist:
                user['is_in_blacklist'] = True
            else:
                user['is_in_blacklist'] = False
        return users

    # Make user
    def make_user(self, id_in):
        qry = "UPDATE Users SET user_type='user' WHERE id=%s;"
        self.mycursor.execute(qry, (id_in, ))
        self.mydb.commit()
        return

    # Make admin
    def make_admin(self, id_in):
        qry = "UPDATE Users SET user_type='admin' WHERE id=%s;"
        self.mycursor.execute(qry, (id_in, ))
        self.mydb.commit()
        return

    # Ban user
    def ban_user(self, id_in):
        qry = "SELECT username FROM Users WHERE id=%s;"
        self.mycursor.execute(qry, (id_in, ))
        username = self.mycursor.fetchone()
        username = username['username']

        qry = "INSERT BlackList VALUES (%s, %s);"
        self.mycursor.execute(qry, (id_in, username))
       
        self.mydb.commit()
        return

    # Unban user
    def unban_user(self, id_in):
        qry = "DELETE FROM BlackList WHERE id=%s;"
        self.mycursor.execute(qry, (id_in, ))
        self.mydb.commit()
        return

    ##########################
    #   Document Management
    ##########################

    # Create document
    def create_doc(self, title_in, owner_in, content_in, is_private_in):
        qry = "INSERT INTO Documents(status, title, owner, content) VALUES (%s, %s, %s, %s);"
        if is_private_in:
            self.mycursor.execute(
                qry, ('private', title_in, owner_in, content_in))
        else:
            self.mycursor.execute(
                qry, ('public', title_in, owner_in, content_in))
        self.mydb.commit()
        return True

    # Edit document, must be followed by edit_hist() function
    def edit_doc(self, id_in, title_in, content_in, is_private_in):
        qry = "UPDATE Documents SET status=%s, title=%s, content=%s, modify_date=now() WHERE id=%s;"
        if is_private_in:
            self.mycursor.execute(
                qry, ('private', title_in, content_in, id_in))
        else:
            self.mycursor.execute(qry, ('public', title_in, content_in, id_in))
        self.mydb.commit()
        return True

    # Write document history after editing, must follow edit_doc() function
    def edit_hist(self, doc_id_in, title_in, user_in, content_in, date_in):
        qry = "INSERT INTO History(doc_id, title, user, content, modify_date) VALUES (%s, %s, %s, %s, %s);"
        self.mycursor.execute(
            qry, (doc_id_in, title_in, user_in, content_in, date_in))
        self.mydb.commit()
        return True

    # Delete document
    def delete_doc(self, id_in):
        qry = "DELETE FROM Documents WHERE id=%s;"
        self.mycursor.execute(qry, (id_in, ))
        self.mydb.commit()
        return True

    #############################
    #       Get Documents
    #############################

    # Get public documents for GUEST (non-user)!!!
    def get_docs_public(self):
        qry = "SELECT * FROM Documents WHERE status='public';"
        self.mycursor.execute(qry)
        docs = self.mycursor.fetchall()
        return docs

    # Get available documents for USER
    def get_docs_user(self, username_in):
        qry = "SELECT * FROM Documents WHERE status='public' OR owner=%s;"
        self.mycursor.execute(qry, (username_in, ))
        docs = self.mycursor.fetchall()
        return docs

    # Get ALL documents for ADMIN
    def get_docs_admin(self):
        qry = "SELECT * FROM Documents;"
        self.mycursor.execute(qry)
        docs = self.mycursor.fetchall()
        return docs

    # Get document history list
    def get_hist_list(self, id_in, username_in):
        # Get doc info by id
        qry = "SELECT * FROM Documents WHERE id = %s;"
        self.mycursor.execute(qry, (id_in, ))
        doc = self.mycursor.fetchone()

        # Get history list by id
        qry = "SELECT * FROM History WHERE doc_id=%s ORDER BY modify_date DESC;"
        self.mycursor.execute(qry, (id_in, ))
        hist_list = self.mycursor.fetchall()

        # Return doc if it's public
        if doc['status'] == "public":
            return hist_list, True

        qry = "SELECT * FROM Users WHERE username = %s;"
        self.mycursor.execute(qry, (username_in, ))
        user = self.mycursor.fetchone()
        if user['user_type'] == "admin":    # Admin gets everything
            return hist_list, True
        elif user['username'] == doc['owner']:  # Doc owner can view the doc
            return hist_list, True
        else:
            return False, False


    # Get document by id
    def get_doc_by_id(self, id_in, username_in=''):
        # Get doc by id
        qry = "SELECT * FROM Documents WHERE id = %s;"
        self.mycursor.execute(qry, (id_in, ))
        doc = self.mycursor.fetchone()

        # Return doc if it's public
        if doc['status'] == "public":
            return doc

        # User not logged in, doesn't have access to doc
        if username_in == '':
            return False

        # User is logged in
        else:
            qry = "SELECT * FROM Users WHERE username = %s;"
            self.mycursor.execute(qry, (username_in, ))
            user = self.mycursor.fetchone()
            if user['user_type'] == "admin":    # Admin gets everything
                return doc
            elif user['username'] == doc['owner']:  # Doc owner can view the doc
                return doc
            else:
                return False


    # Get history version document by id
    def get_doc_hist_by_id(self, record_id_in, username_in=''):
        # Get doc hist by id
        qry = "SELECT * FROM History WHERE record_id = %s;"
        self.mycursor.execute(qry, (record_id_in, ))
        doc_hist = self.mycursor.fetchone()

        # Get doc info by id
        qry = "SELECT * FROM Documents WHERE id = %s;"
        self.mycursor.execute(qry, (doc_hist['doc_id'], ))
        doc = self.mycursor.fetchone()

        # Return doc if it's public
        if doc['status'] == "public":
            return doc_hist

        # User not logged in, doesn't have access to doc
        if username_in == '':
            return False

        # User is logged in
        else:
            qry = "SELECT * FROM Users WHERE username = %s;"
            self.mycursor.execute(qry, (username_in, ))
            user = self.mycursor.fetchone()
            if user['user_type'] == "admin":    # Admin gets everything
                return doc_hist
            elif user['username'] == doc['owner']:  # Doc owner can view the doc
                return doc_hist
            else:
                return False
