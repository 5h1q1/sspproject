from User import User
class Staff(User):

    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role, position, address):
        super().__init__(first_name, last_name, email, phone_number, password, gender, age, role)
        self.__position = position
        self.__address = address
        self.__role = "Staff"

    def set_role(self, role):
        self.__role = role

    def set_position(self, position):
        self.__position = position

    def set_address(self, address):
        self.__address = address

    def get_position(self):
        return self.__position

    def get_address(self):
        return self.__address

    def check_password(self, entered_password):
        return self.get_password() == entered_password
