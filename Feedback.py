from Customer import *

class Feedback(Customer):
    count_id = 0

    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role, date_made, remarks):
        super().__init__(first_name, last_name, email, phone_number, password, gender, age, role)
        Feedback.count_id += 1
        self.__feedback_id = Feedback.count_id
        self.__remarks = remarks
        self.__date_made = date_made

    def get_feedback_id(self):
        return self.__feedback_id

    def get_remarks(self):
        return self.__remarks

    def get_date_made(self):
        return self.__date_made

    def set_feedback_id(self, feedback_id):
        self.__feedback_id = feedback_id

    def set_remarks(self, date_made):
        self.__date_made = date_made
