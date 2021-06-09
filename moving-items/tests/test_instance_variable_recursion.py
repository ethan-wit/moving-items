class class_return():

    def __init__(self):

        self.__change_user = None

    def returning(self):

        user_input = input('1 input: ')
        if user_input == 1:
            self.returning()
        else:
            return user_input

class instance_var():

    def __init__(self):
        self.__user = None

    returner = class_return()
    self.__user = returner.returning()

    print(self.__user)
    


def main():

    instance_var()

