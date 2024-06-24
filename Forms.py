from wtforms import Form, StringField, RadioField, SelectField, TextAreaField, PasswordField, IntegerField, validators
from wtforms.fields import EmailField, DateField, HiddenField, SubmitField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired, Regexp
from flask_wtf import FlaskForm
from datetime import datetime, date


def validate_date(form, field):
    today = datetime.now().date()
    if field.data < today:
        raise validators.ValidationError('Please select a date on or after today.')


def validate_date_range(form, field):
    min_date = date(1934, 1, 1)
    max_date = date(2014, 12, 31)
    if field.data < min_date or field.data > max_date:
        raise validators.ValidationError('Date must be between 1934 and 2014')

class CreateCustomerForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.data_required(), validators.Length(max=8, message="Please enter a valid Singapore phone number (e.g., 91234567)"), validators.Regexp(r"^[689]\d{7}$", message="Invalid Singapore phone number")])
    password = PasswordField('Password', [validators.DataRequired()])
    gender = SelectField('Gender', [validators.optional()], choices=[('N/A', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    age = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date_range])
    role = HiddenField(default="Customer")
    submit = SubmitField('Update Profile')

class CreateStaffForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.data_required(), validators.Length(max=8, message="Please enter a valid Singapore phone number (e.g., 91234567)"), validators.Regexp(r"^[689]\d{7}$", message="Invalid Singapore phone number")])
    password = PasswordField('Password', [validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('F', 'Female'), ('M', 'Male')], default='')
    age = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date_range])
    position = SelectField('Position', [validators.DataRequired()], choices=[('Cashier', 'Cashier'), ('Manager', 'Manager'), ('Waiter/Waitress', 'Waiter/Waitress')], default='')
    address = StringField('Address', [validators.DataRequired()])
    role = HiddenField(default="Staff")

class CreateAdminForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.data_required(), validators.Length(max=8, message="Please enter a valid Singapore phone number (e.g., 91234567)"), validators.Regexp(r"^[689]\d{7}$", message="Invalid Singapore phone number")])
    password = PasswordField('Password', [validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('F', 'Female'), ('M', 'Male')], default='')
    age = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date_range])
    address = StringField('Address', [validators.DataRequired()])
    role = HiddenField(default="Admin")

class CreateFeedbackForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.data_required(), validators.Length(max=8, message="Please enter a valid Singapore phone number (e.g., 91234567)"), validators.Regexp(r"^[689]\d{7}$", message="Invalid Singapore phone number")])
    password = HiddenField(default="")
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    age = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date_range])
    role = HiddenField(default="Customer")
    date_made = HiddenField(default=datetime.now().strftime('%Y-%m-%d'))
    remarks = TextAreaField('Feedback', [validators.Optional()])

class CreateCharityForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    charity_name = StringField('Charity Organization', [validators.Length(min=1, max=150), validators.DataRequired()])
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')],
                         default='')
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    date_made = DateField('Date of Delivery', format='%Y-%m-%d')
    remarks = TextAreaField('Remarks', [validators.Optional()])

class PaymentForm(Form):
    card_number = StringField('Card Number (16 Digit Number)', [validators.Length(min=16, max=16), validators.DataRequired(), validators.Regexp(regex='^[0-9]+$', message="Card Number must be a 16 digit number")])
    cardholder_name = StringField('Cardholder Name', validators=[DataRequired(), Regexp('^[a-zA-Z]+$', message='Cardholder name should contain only letters.')])

    def validate_expiry_date(form, field):
        if getattr(field, '_expiry_date_validated', False):
            return

        error_messages = []
        try:
            # Attempt to parse the date
            date_obj = datetime.strptime(field.data, '%m%y')
            # Check if the date is in the future
            if date_obj < datetime.now():
                error_messages.append('Expiry Date must be in the future')
        except ValueError:
            # If parsing fails, field.data is not a valid date format
            if any(char.isalpha() for char in field.data):
                error_messages.append('Invalid characters in the Expiry Date')
            else:
                error_messages.append('Invalid date format. Please use MMYY')

        if error_messages:
            field.errors.extend(error_messages)
            field._expiry_date_validated = True


    expiry_date = StringField('Expiry Date (MMYY in Numbers)', [validators.Length(min=4, max=4), validators.DataRequired(), validate_expiry_date])
    cvc = StringField('CVC (3 Digit Number)',[validators.Length(min=3, max=3), validators.DataRequired(), validators.Regexp(regex='^[0-9]+$', message="CVC must be a 3 digit number")])
    submit = SubmitField('Place Order')

class EditOrderForm(Form):
    item = StringField('Items', render_kw={'readonly': True})
    total_price = FloatField('Price', render_kw={'readonly': True})
    submit = SubmitField('Update Order')

class EditOrderItemForm(Form):
    quantity = IntegerField('Quantity', validators=[DataRequired(), validators.NumberRange(min = 0, max = 10, message= "Enter a valid quantity value")])

class EditOrderMainForm(EditOrderForm):
    items = FieldList(FormField(EditOrderItemForm))

class EditOrderInputForm(FlaskForm):
    order_id_to_edit = IntegerField('Order ID to Edit',[validators.NumberRange(min=1, message="Please enter a valid order ID")],
        render_kw={"placeholder": "Enter Order ID"})
    submit = SubmitField('Edit Order')

class CreateBookForm(Form):
    first_name = StringField('First Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    last_name = StringField('Last Name', [validators.Length(min=1, max=150), validators.DataRequired()])
    email = EmailField('Email', [validators.Email(), validators.DataRequired()])
    phone_number = StringField('Phone Number', validators=[validators.data_required(), validators.Length(max=8, message="Please enter a valid Singapore phone number (e.g., 91234567)"), validators.Regexp(r"^[689]\d{7}$", message="Invalid Singapore phone number")])
    password = HiddenField(default="")
    gender = SelectField('Gender', [validators.DataRequired()], choices=[('', 'Select'), ('F', 'Female'), ('M', 'Male')], default='')
    age = DateField('Date of Birth', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date_range])
    party_size = SelectField('Party size', choices=[(1, '1 pax'), (2, '2 pax'), (3, '3 pax'), (4, '4 pax')], default='')
    date = DateField('Date', format='%Y-%m-%d', validators=[validators.DataRequired(), validate_date])
    time_slot = RadioField('Time slot', choices=[(10, '10am'), (11, '11am'), (12, '12pm'), (13, '1pm'),
                                                 (14, '2pm'), (15, '3pm'), (16, '4pm'), (17, '5pm'),
                                                 (18, '6pm')], default='')
    comments = TextAreaField('Comments', [validators.Optional()])
    booking_status = SelectField('Booking Status', choices=[('Reserved', 'Reserved'), ('Seated', 'Seated'), ('Late', 'Late')], default='Reserved')

