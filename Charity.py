class Charity():
    count_id = 0

    def __init__(self, first_name, last_name, charity_name, gender, email, date_made, remarks):
        Charity.count_id += 1
        self.__charity_id = Charity.count_id
        self.__first_name = first_name
        self.__last_name = last_name
        self.__charity_name = charity_name
        self.__gender = gender
        self.__email = email
        self.__date_made = date_made
        self.__remarks = remarks

    def get_charity_id(self):
        return self.__charity_id

    def get_first_name(self):
        return self.__first_name

    def get_last_name(self):
        return self.__last_name

    def get_charity_name(self):
        return self.__charity_name

    def get_date_joined(self):
        return self.__date_made

    def get_gender(self):
        return self.__gender

    def get_email(self):
        return self.__email

    def get_date_made(self):
        return self.__date_made

    def get_remarks(self):
        return self.__remarks

    def set_charity_id(self, charity_id):
        self.__charity_id = charity_id

    def set_first_name(self, first_name):
        self.__first_name = first_name

    def set_last_name(self, last_name):
        self.__last_name = last_name

    def set_charity_name(self, charity_name):
        self.__charity_name = charity_name

    def set_date_made(self, date_made):
        self.__date_made = date_made

    def set_gender(self, gender):
        self.__gender = gender

    def set_email(self, email):
        self.__email = email

    def set_remarks(self, remarks):
        self.__remarks = remarks
