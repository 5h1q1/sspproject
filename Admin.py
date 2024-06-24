from User import User
import shelve
from datetime import *
class Admin(User):

# elgin test lol no its zikri
    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role, address):
        super().__init__(first_name, last_name, email, phone_number, password, gender, age, role)
        self.__address = address
        self.__role = "Admin"

    def set_role(self, role):
        self.__role = role

    def set_address(self, address):
        self.__address = address

    def get_address(self):
        return self.__address

    def check_password(self, entered_password):
        return self.get_password() == entered_password

# Create a User object (user1)
user1 = Admin(
    first_name="John",
    last_name="Doe",
    email="JohnDoe@gmail.com",
    phone_number="81234567",
    password="123",
    gender="M",
    age=datetime.strptime("1990-01-01", "%Y-%m-%d").date(),
    role="Admin",
    address="180 Ang Mo Kio Ave 8, Singapore 569830"
)

# Open the admin database (assuming 'admin.db' is the shelve file for the admin database)
admin_db = shelve.open('admin.db', writeback=True)

# Check if 'Admins' key exists, create it if not
if 'Admins' not in admin_db:
    admin_db['Admins'] = {}

# Add user1 to the 'Admins' dictionary
admin_db['Admins'][user1.get_user_id()] = user1

# Save changes and close the shelve file
admin_db.close()
