from User import User
import os

def load_order_id_counter():
    counter_file = 'order_id_counter.txt'
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as f:
            return int(f.read())
    else:
        return 0

def save_order_id_counter(counter):
    counter_file = 'order_id_counter.txt'
    with open(counter_file, 'w') as f:
        f.write(str(counter))

class Customer(User):

    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role):
        super().__init__(first_name, last_name, email, phone_number, password, gender, age, role)
        self.__loyalty = 0
        self.__password = password
        self._payment_info = {}
        self._orders = []
        self.__role = "Customer"

    def get_loyalty(self):
        return self.__loyalty

    def set_loyalty(self, loyalty):
        self.__loyalty = loyalty

    def set_role(self, role):
        self.__role = role

    def check_password(self, entered_password):
        return self.get_password() == entered_password

    @property
    def payment_info(self):
        return self._payment_info

    @payment_info.setter
    def payment_info(self, value):
        self._payment_info = value

    @property
    def orders(self):
        return self._orders

    def update_loyalty(self, total_price):
        loyalty_points = total_price / 10
        new_loyalty = self.get_loyalty() + loyalty_points
        self.set_loyalty(new_loyalty)

    def add_order(self, item, quantity, total_price):
        order_id_counter = load_order_id_counter()
        order_id_counter += 1
        print(f"After placing order - Order ID Counter: {order_id_counter}")

        order_data = {
            'order_id': order_id_counter,
            'item': item,
            'quantity': quantity,
            'total_price': total_price,
        }
        self._orders.append(order_data)

        # Update loyalty points when adding an order
        self.update_loyalty(total_price)

        save_order_id_counter(order_id_counter)

    def update_payment_info(self, card_number, cardholder_name, expiry_date, cvc):
        self._payment_info = {
            'cardNumber': card_number,
            'cardholderName': cardholder_name,
            'expiryDate': expiry_date,
            'cvc': cvc
        }
