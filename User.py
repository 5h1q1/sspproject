from datetime import datetime
class User:
    count_id = 0

    # initializer method
    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role):
        User.count_id += 1
        self.__user_id = User.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__phone_number = phone_number
        self.__password = password
        self.__gender = gender
        self.__age = age
        self.__role = role

    # accessor methods
    def get_user_id(self):
        return self.__user_id

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_email(self):
        return self.__email

    def get_phone_number(self):
        return self.__phone_number

    def get_password(self):
        return self.__password

    def get_gender(self):
        return self.__gender

    def get_age(self):
        return self.__age

    def get_role(self):
        return self.__role

    # mutator methods
    def set_user_id(self, user_id):
        self.__user_id = user_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name

    def set_email(self, email):
        self.__email = email

    def set_phone_number(self, phone_number):
        self.__phone_number = phone_number

    def set_gender(self, gender):
        self.__gender = gender

    def set_age(self, age):
        self.__gender = age

    def set_password(self, password):
        self.__password = password

    def check_password(self, entered_password):
        return self.__password == entered_password


