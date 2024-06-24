from datetime import datetime, time
from Customer import *
class Book(Customer):
    count_id = 0
    _hour = datetime.now().hour

    def __init__(self, first_name, last_name, email, phone_number, password, gender, age, role, party_size, date, time_slot, comments, booking_status):
        super().__init__(first_name, last_name, email, phone_number, password, gender, age, role)
        Book.count_id += 1
        self._book_id = Book.count_id
        self._party_size = party_size
        self._date = self.convert_to_date(date)
        self._time_slot = time_slot
        self._comments = comments
        self._booking_status = booking_status
        self._time = datetime.now()
        self._available_seats = 0

    def get_book_id(self):
        return self._book_id

    def get_party_size(self):
        return self._party_size

    def get_date(self):
        return self._date

    def get_time_slot(self):
        return self._time_slot

    def get_comments(self):
        return self._comments

    def get_booking_status(self):
        return self._booking_status

    def get_time(self):
        return self._time

    def set_book_id(self, book_id):
        self._book_id = book_id

    def set_party_size(self, party_size):
        self._party_size = party_size

    def set_date(self, date):
        self._date = self.convert_to_date(date)

    def set_time_slot(self, time_slot):
        self._time_slot = time_slot

    def set_comments(self, comments):
        self._comments = comments

    def set_booking_status(self, booking_status):
        self._booking_status = booking_status

    def get_available_seats(self):
        return self._available_seats

    def removing_booking_seats(self, party_size):
        self._available_seats += party_size

    def update_booking_status(self):
        current_time = datetime.now()

        # Convert self._time_slot to an integer
        time_slot = int(self._time_slot)

        # Create a datetime.time object
        booking_time = time(time_slot, 0)

        # Combine date and time components
        booking_datetime = datetime.combine(self._date, booking_time)

        # Check if the current time has passed the booking time
        if current_time > booking_datetime:
            self._booking_status = "Late"
        else:
            self._booking_status = "Reserved"

    def confirm_booking_seats(self, party_size):
        party_size = int(party_size)
        self._available_seats -= party_size

    @staticmethod
    def convert_to_date(date_str):
        return datetime.strptime(date_str, '%Y-%m-%d').date()
