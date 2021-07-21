import pandas as pd 
import sqlite3
import getpass
import hashlib
import random
import functools
import sys
import time
import re 


###################################
#Add to main dictionary
#####################################

#create (if not exist) sqlite tables
#create_new_item(self, user, item_name, desired_quantity, quantity)

#read_user_items(self, user)
#read_item_quantity_desired(self, user, item_name)

#update_desired_quantity(self, user, desired_quantity, new_desired_quantity)
#update_quantity(self, user, quantity, new_quantity)
#update_clear_quantities(self, user)

#delete_item(self, user, item_name)


class MovingItems:
    '''
    Object that performs CRUD operations on a sqlite database of users' items they wish to bring when moving dorms/apartments.
    '''


    def __init__(self, user):
        '''
        Constructs a moving items object.
        Sets self.__user instance variable to Authenticator login return, which allows for CRUD operations on user's database items.
        @param self.__user: username in database users table
        '''

        #user instance variable
        self.__user = user
        #Connect to db, create cursor
        self.__conn = sqlite3.connect('moving-items.db')
        self.__cursor = self.__conn.cursor()
        self.item_sql = '''
        SELECT ITEM_ID FROM items WHERE ITEM = (?)
        '''


    def get_item_id(self, item_input):
        '''
        Gets ITEM_ID from database, with item name input as parameter
        '''

        #Execute select statement, cursor stores data
        self.__cursor.execute(self.item_sql, (item_input,))
        #Get the first row from the cursor
        inserted_item_row = self.__cursor.fetchone()
        #Get the first (zeroth) column value from the row
        inserted_item_id = inserted_item_row[0]

        return inserted_item_id


    def db_decorator(meth):
        '''
        decorator for CRUD methods
        '''

        @functools.wraps(meth)
        def db_commit(self, *args, **kwargs):
            '''
            Commits changes to database
            '''

            meth_return = meth(self, *args, **kwargs)

            #Commit to db
            self.__conn.commit()

            return meth_return

        return db_commit


    @db_decorator
    def create_new_item(self):
        '''
        Inserts new item in items table, and inserts corresponding item, user, desired quantity, quantity in users_items table
        '''

        item_name = input('Please input the item you would like to add to your list: ')
        desired_quantity = input('Please input the desired quantity of this item: ')
        quantity = input('Please input the current quantity held for this item: ')

        add_item_sql = '''
        INSERT OR REPLACE INTO items (ITEM) VALUES (?)
        '''
        self.__cursor.execute(add_item_sql, (item_name,))

        #Item ID
        inserted_item_id = self.get_item_id(item_name)

        add_user_item_sql = '''
        INSERT INTO users_items (USER_ID, ITEM_ID, DESIRED_QUANTITY, QUANTITY) VALUES (?,?,?,?)
        '''
        self.__cursor.execute(add_user_item_sql, (self.__user, inserted_item_id, desired_quantity, quantity,))

        print(f'{item_name} has been added to your list')


    def read_user_items(self):
        '''
        Prints all user's rows in user_items table
        '''
        read_user_items_sql = '''
        SELECT l.USER_ID, r.ITEM, l.DESIRED_QUANTITY, l.QUANTITY 
        FROM users_items l 
        INNER JOIN items r ON l.ITEM_ID = r.ITEM_ID 
        WHERE l.USER_ID = ?
        '''

        for row in self.__cursor.execute(read_user_items_sql, (self.__user,)):
            print(row)


    def read_item_quantity_and_desired(self):
        '''
        Prints the user's quantity and desired quantity of an item
        '''
        item_name = input('Please input the item you would like to get the recorded "quantity" and "desired quantity" for: ')

        #Get item ID
        inserted_item_id = self.get_item_id(item_name)

        read_item_quantity_sql = '''
        SELECT l.USER_ID, r.ITEM, l.DESIRED_QUANTITY, l.QUANTITY 
        FROM users_items l
        INNER JOIN items r ON l.ITEM_ID = r.ITEM_ID
        WHERE l.USER_ID = ? AND l.ITEM_ID = ?
        '''

        for row in self.__cursor.execute(read_item_quantity_sql, (self.__user, inserted_item_id)):
            print(row)


    @db_decorator
    def update_desired_quantity(self):

        item_name = input('Please input the name of the item for which you would like to change the desired quantity: ')
        new_desired_quantity = inpute("Please input the item's new desired quantity: ")

        #Get item ID
        inserted_item_id = self.get_item_id(item_name)

        update_item_desired_quantity_sql = '''
        UPDATE users_items
        SET DESIRED_QUANTITY = ?
        WHERE USER_ID = ? AND ITEM_ID = ?
        '''

        try:
            self.__cursor.execute(update_item_desired_quantity_sql, (new_desired_quantity, self.__user, inserted_item_id))
        except:
            print(f'Could not change desired quantity of {item_name}')


    @db_decorator
    def update_quantity(self):

        item_name = input('Please input the name of the item for which you would like to change the quantity: ')
        new_quantity = inpute("Please input the item's new quantity: ")

        #Get item ID
        inserted_item_id = self.get_item_id(item_name)

        update_item_quantity_sql = '''
        UPDATE users_items
        SET QUANTITY = ?
        WHERE USER_ID = ? AND ITEM_ID = ?
        '''

        try:
            self.__cursor.execute(update_item_quantity_sql, (new_quantity, self.__user, inserted_item_id))
        except:
            print(f'Could not change quantity of {item_name}')
    

    @db_decorator
    def update_quantities_0(self):

        confirm = input('Please input "yes" if you would like to set all your item quantities to zero. Please input "no" otherwise: ')

        if confirm == "yes":
            update_quantities_0_sql = '''
            UPDATE users_items
            SET QUANTITY = 0
            WHERE USER_ID = ?
            '''
            self.__cursor.execute(update_quantities_0_sql, (self.__user))
        elif confirm == 'no':
            print("Understood. No action will be taken.")
            pass
        else:
            print("Invalid input. No action will be taken.")
            pass


    @db_decorator
    def delete_item(self):

        item_name = input('Please input the name of the item for which you would like to delete from your list: ')

        #Get item ID
        inserted_item_id = self.get_item_id(item_name)

        delete_item_sql = '''
        DELETE FROM users_items
        WHERE USER_ID = ? AND ITEM_ID = ?
        '''
        self.__cursor.execute(delete_item_sql, (self.__user, inserted_item_id))


    def logoff(self):

        print('You will now be logged off, and the program will end.')
        self.__conn.close()
        time.sleep(4)
        sys.exit()


class Authenticator(): 
    '''
    Allows user to log in or sign up. 
    '''


    def __init__(self):

        #class variables for user 
        self.__username = None
        self.__password = None
        self.__conn = sqlite3.connect('moving-items.db')
        self.__cursor = self.__conn.cursor()


    def greeting(self):
        '''
        Asks user if they would like to log in or sign up, until valid string is input.
        Initiatites _signup() or _login() methods if options are chosen.
        '''

        login_signup_decision = input('Would you like to "signup" or "login": ')
        while not ((login_signup_decision != "signup") | (login_signup_decision != "login")):
            login_signup_decision = input('You did not input "signup" or "login". Please input one of these options: ')
            time.sleep(2)

        if login_signup_decision == "signup":
            self._signup()
            login_response = input('Would you now like to log in? Please respond either "yes" or "no".')
            if login_response == "yes":
                return self._login()
            elif login_response == "no":
                print("Thank you. The program will now end.")
                time.sleep(2)
                sys.exit()
            else:
                print("Invalid response. The program will now end.")
                time.sleep(2)
                sys.exit()

        elif login_signup_decision == "login":
            return self._login()


    def _no_dup_username(self):
        '''
        Create new username (8 integers) that is unique in list of existing usernames
        '''

        #Generate random username
        rand_username = random.randint(10000000,99999999)

        #Ensure rand_username isn't already in use
        get_usernames = '''
        SELECT USERNAME
        FROM users
        '''
        self.__cursor.execute(get_usernames)
        usernames = self.__cursor.fetchall()

        while rand_username in usernames:

            rand_username = random.randint(10000000,99999999)

        return rand_username 


    def _signup(self):
        '''
        Adds user's username (autogenerated) and password (hashed) to user table in sqlite database.
        '''

        #Create unique username
        self.__username = self._no_dup_username()

        #Input password
        self.__password = getpass.getpass('Please input your new password. It must be 8-10 characters, include one upper-case letter, one lower-case letter, one number, and one special character (e.g. %*$): ')

        #Enforce criteria
        while re.search("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,10}$", self.__password) == None:
            self.__password = getpass.getpass('Password did not meet criteria. Please input your new password. It must be 8-10 characters, include one upper-case letter, one lower-case letter, one number, and one special character (e.g. %*$): ')
            time.sleep(5)

        print(f'Thank you. Your password meets the critera. You have been assigned the username: {self.__username}. Please remember your username and password, as they will be required to log in.')
        #Hash password (should also salt if placed into production)
        hashed_password = hashlib.sha256(self.__password.encode('utf-8')).hexdigest()
        #Place username & hashed password into users table
        insert_username_password = '''
        INSERT INTO users VALUES (?,?)
        '''
        self.__cursor.execute(insert_username_password, (self.__username, hashed_password,))
        self.__conn.commit()
        self.__conn.close()


    def _login(self):
        '''
        Logs in user, such that they can perform CRUD operations on their database items.
        '''

        if self.__username == None or self.__password == None:

            self.__username = input('Please input your user ID: ')
            self.__password = getpass.getpass('Please input your password: ')

        #Get match input username to a username in users table
        match_username = '''
        SELECT USERNAME FROM users WHERE USERNAME = ?
        '''
        self.__cursor.execute(match_username, (self.__username,))
        match_row_username = self.__cursor.fetchone()

        #Get match input username to a username in users table
        match_password = '''
        SELECT PASSWORD FROM users WHERE PASSWORD = ?
        '''
        self.__cursor.execute(match_password, (hashlib.sha256(self.__password.encode('utf-8')).hexdigest(),))
        match_row_password = self.__cursor.fetchone()

        self.__conn.close()

        if (match_row_username == None):
            print("Matching username not found. Program will end, but please feel free to try again.")
            time.sleep(5)
            sys.exit()

        elif (match_row_username != None):
            print('User found.')

            if (match_row_password != None):
                print('Password accepted. User logged in.')
                return self.__username

            else:
                print("Matching password not found. This program will end, but please feel free to try again.")
                time.sleep(5)
                sys.exit()


def create_db_tables():

    #Connect to db
    conn = sqlite3.connect('moving-items.db')
    cursor = conn.cursor()

    #Create (if not exist) items table
    items_table = '''
    CREATE TABLE IF NOT EXISTS items(
    ITEM_ID INTEGER PRIMARY KEY,
    ITEM TEXT
    )
    '''
    cursor.execute(items_table)

    #Create (if not exist) users table in db
    create_users_table = '''
    CREATE TABLE IF NOT EXISTS users(
    USERNAME INTEGER PRIMARY KEY,
    PASSWORD TEXT
    )
    '''
    cursor.execute(create_users_table)
    
    #Create (if not exist) users_items table
    create_users_items_table = '''
    CREATE TABLE IF NOT EXISTS users_items(
    USERS_ITEMS_ID INTEGER PRIMARY KEY,
    USER_ID INTEGER,
    ITEM_ID INTEGER,
    DESIRED_QUANTITY INTEGER,
    QUANTITY INTEGER,
    FOREIGN KEY(USER_ID) REFERENCES users(USERNAME),
    FOREIGN KEY(ITEM_ID) REFERENCES items(ITEM_ID)
    )
    '''
    cursor.execute(create_users_items_table)

    #Commit and disconnect from db
    conn.commit()
    conn.close()


if __name__ == "__main__":

    '''
    The main function is a CRUD app (inputs from command line) that interacts with a sqlite3 db, 
    with the purpose of cataloging necessary items to bring when moving or going on a trip.
    '''

    #create (if not exist) db tables
    create_db_tables()

    #singup/login prompting object
    authentication = Authenticator()
    user = authentication.greeting()

    #user interface object
    crud = MovingItems(user)
    
    #dict of user input keys with method values
    crud_dict = {'input new item' : 'create_new_item', 'view items' : 'read_user_items', "view item's quantity and desired quantity" : 'read_item_quantity_and_desired', "update item's desired quantity" : 'update_desired_quantity', "update item's quantity" : 'update_quantity', "clear item quantities" : 'update_quantities_0', 'delete item' : 'delete_item'}
    
    #user method input
    def user_input():
        user_method_input = input('''Please input the action you would like to take. The options are listed below:\n
        input new item\n
        view items\n
        view item's quantity and desired quantity\n
        update item's desired quantity\n
        update item's quantity\n
        clear item quantities\n
        delete item\n
        log off

        ''')
        return user_method_input
    
    #user input
    user_method_input = user_input()
    time.sleep(1)

    while user_method_input != 'log off':

        if user_method_input in crud_dict.keys():
            #Execute chosen action
            crud_method = crud_dict.get(user_method_input)
            crud_method = "." + crud_method + '()'
            crud_exec = "crud" + crud_method
            exec(crud_exec)

        else:
            print('Invalid action. You must input an action from the list.')

        #re-init user input
        print('\n')
        user_method_input = user_input()
        time.sleep(1)


    if user_method_input == 'log off':
        print('\n')
        time.sleep(1)
        crud.logoff()









