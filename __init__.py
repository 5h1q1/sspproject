from flask import Flask, render_template, request, redirect, url_for, session, flash
from Forms import CreateCustomerForm, CreateStaffForm, CreateAdminForm, CreateFeedbackForm, CreateCharityForm, PaymentForm, EditOrderMainForm, EditOrderInputForm, CreateBookForm
import shelve, Customer, Staff, Admin, Feedback, Charity, Book, os
import logging
import dbm
from flask_mail import Message, Mail
from datetime import datetime
from werkzeug.utils import secure_filename
from Customer import *


app = Flask(__name__, static_url_path='/static')
app.config['WTF_CSRF_ENABLED'] = False
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads'  # Define the folder where uploaded images will be stored
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logging.basicConfig(level=logging.DEBUG)

def authenticate_user(email, password, user_role, user_dict):
    user = next(
        (customer_data for customer_data in user_dict.values() if customer_data.get_email().lower() == email.lower()),
        None
    )
    if user and user.check_password(password):
        session['user_role'] = user_role
        session['user_id'] = user.get_user_id()
        session['user_email'] = user.get_email()
        return True
    return False

@app.route('/Login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            with shelve.open('customer.db', 'r') as customer_db:
                customers_dict = customer_db.get('Customers', {})
                customer = next(
                    (customer_data for customer_data in customers_dict.values() if customer_data.get_email().lower() == email.lower()),
                    None)
                if customer and customer.check_password(password):
                    session['user_role'] = 'customer'
                    session['user_id'] = customer.get_user_id()
                    session['user_email'] = customer.get_email()
                    return redirect(url_for('home'))

            with shelve.open('staff.db', 'r') as staff_db:
                staff_dict = staff_db.get('StaffMembers', {})
                staff_member = next(
                    (customer_data for customer_data in staff_dict.values() if customer_data.get_email().lower() == email.lower()),
                    None)
                if staff_member and staff_member.check_password(password):
                    session['user_role'] = 'staff'
                    session['user_id'] = staff_member.get_user_id()
                    session['user_email'] = staff_member.get_email()
                    return redirect(url_for('dashboard'))

            with shelve.open('admin.db', 'r') as admin_db:
                admin_dict = admin_db.get('Admins', {})
                admin_member = next(
                    (customer_data for customer_data in admin_dict.values() if customer_data.get_email().lower() == email.lower()),
                    None)
                if admin_member and admin_member.check_password(password):
                    session['user_role'] = 'admin'
                    session['user_id'] = admin_member.get_user_id()
                    session['user_email'] = admin_member.get_email()
                    return redirect(url_for('dashboard'))

            error = 'Invalid email or password. Please try again.'

        except Exception as e:
            app.logger.error(f'Error accessing user databases: {str(e)}')
            error = 'An internal error occurred. Please try again later.'

    if error:
        flash(error, 'error')

    return render_template('Website/Login.html')

@app.route('/Logout')
def logout():
    session.pop('user_role', None)
    session.pop('user_id', None)
    session.pop('user_email', None)
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

def create_database_if_not_exist(db_filename, initial_data):
    try:
        with shelve.open(db_filename, 'c') as db:
            if not db:
                db.update(initial_data)
    except Exception as e:
        app.logger.error(f'Error creating database {db_filename}: {str(e)}')

create_database_if_not_exist('customer.db', {'Customers': {}})
create_database_if_not_exist('staff.db', {'StaffMembers': {}})
create_database_if_not_exist('admin.db', {'Admins': {}})
create_database_if_not_exist('feedback.db', {'Feedback': {}})
create_database_if_not_exist('charity.db', {'Charity': {}})
create_database_if_not_exist('book.db', {'Books': {}})

@app.route('/Charity', methods=['GET', 'POST'])
def create_charity():
    create_charity_form = CreateCharityForm(request.form)
    if request.method == 'POST' and create_charity_form.validate():
        charity_dict = {}
        db = shelve.open('charity.db', 'c')

        try:
            charity_dict = db['Charity']
        except:
            print('Error in retrieving Charity enquires from charity.db')

        charity = Charity.Charity(create_charity_form.first_name.data,
                                  create_charity_form.last_name.data,
                                  create_charity_form.charity_name.data,
                                  create_charity_form.gender.data,
                                  create_charity_form.email.data,
                                  create_charity_form.date_made.data,
                                  create_charity_form.remarks.data)

        charity_dict[charity.get_charity_id()] = charity
        db['Charity'] = charity_dict

        db.close()
        send_invoice_email(charity)

        flash('Feedback submitted successfully. Thank you!', 'success')

        return redirect(url_for('home'))
    return render_template('Website/Charity.html', form=create_charity_form)

@app.route('/RetrieveCharity')
def retrieve_charity():
    charity_dict = {}
    try:
        db = shelve.open('charity.db', 'r')
        charity_dict = db.get('Charity', {})
    except KeyError:
        print("KeyError: 'Charity' not found in the shelve database.")

    db.close()

    return render_template('Dashboard/RetrieveCharity.html', charity_dict=charity_dict)

@app.route('/UpdateCharity/<int:id>/', methods=['GET', 'POST'])
def update_charity(id):
    update_charity_form = CreateCharityForm(request.form)
    if request.method == 'POST' and update_charity_form.validate():
        charity_dict = {}
        db = shelve.open('charity.db', 'w')
        charity_dict = db['Charity']

        charity = charity_dict.get(id)
        charity.set_first_name(update_charity_form.first_name.data)
        charity.set_last_name(update_charity_form.last_name.data)
        charity.set_charity_name(update_charity_form.charity_name.data)
        charity.set_gender(update_charity_form.gender.data)
        charity.set_date_made(update_charity_form.date_made.data)
        charity.set_email(update_charity_form.email.data)
        charity.set_remarks(update_charity_form.remarks.data)

        db['Charity'] = charity_dict
        db.close()

        return redirect(url_for('retrieve_charity'))
    else:
        charity_dict = {}
        db = shelve.open('charity.db', 'r')
        charity_dict = db['Charity']
        db.close()

        charity = charity_dict.get(id)
        update_charity_form.first_name.data = charity.get_first_name()
        update_charity_form.last_name.data = charity.get_last_name()
        update_charity_form.charity_name.data = charity.get_charity_name()
        update_charity_form.gender.data = charity.get_gender()
        update_charity_form.date_made.data = charity.get_date_made()
        update_charity_form.email.data = charity.get_email()
        update_charity_form.remarks.data = charity.get_remarks()


        return render_template('Dashboard/UpdateCharity.html', form=update_charity_form)

@app.route('/DeleteCharity/<int:id>', methods=['POST'])
def delete_Charity(id):
    charity_dict = {}
    db = shelve.open('charity.db', 'w')
    charity_dict = db['Charity']

    charity_dict.pop(id)

    db['Charity'] = charity_dict
    db.close()

    return redirect(url_for('retrieve_charity'))


@app.route('/Feedback', methods=['GET', 'POST'])
def create_feedback():
    create_feedback_form = CreateFeedbackForm(request.form)

    # If the user is logged in, pre-fill the form fields
    if session.get('user_id') and session.get('user_role'):  # Check user role as well
        user = get_user_by_id(session.get('user_id'), session.get('user_role'))
        if user:
            create_feedback_form.first_name.data = user.get_first_name()
            create_feedback_form.last_name.data = user.get_last_name()
            create_feedback_form.email.data = user.get_email()
            create_feedback_form.phone_number.data = getattr(user, 'get_phone_number', '')()
            create_feedback_form.password.data = user.get_password()
            create_feedback_form.gender.data = user.get_gender()
            create_feedback_form.age.data = user.get_age()

    if request.method == 'POST' and create_feedback_form.validate():
        feedback_dict = {}
        db = shelve.open('feedback.db', 'c')

        try:
            feedback_dict = db['Feedback']
        except:
            print("Error in retrieving Feedback from feedback.db")

        # Get the current date and time
        current_date = datetime.now()

        # Format the date as 'Y-M-D'
        formatted_date = current_date.strftime('%Y-%m-%d')

        # Get user ID from session
        user_id = session.get('user_id') if session else 0

        feedback = Feedback.Feedback(
            create_feedback_form.first_name.data,
            create_feedback_form.last_name.data,
            create_feedback_form.email.data,
            create_feedback_form.phone_number.data,
            create_feedback_form.password.data,
            create_feedback_form.gender.data,
            create_feedback_form.age.data,
            session.get('user_role') if session else '',  # Add user role to feedback instantiation
            formatted_date,  # Use the formatted date
            create_feedback_form.remarks.data
        )
        feedback_dict[feedback.get_feedback_id()] = feedback
        db['Feedback'] = feedback_dict

        db.close()
        send_invoice_email(feedback)

        flash('Feedback submitted successfully. Thank you!', 'success')

        return redirect(url_for('home'))

    return render_template('Website/Feedback.html', form=create_feedback_form)

@app.route('/RetrieveFeedback')
def retrieve_feedback():
    feedback_dict = {}
    try:
        db = shelve.open('feedback.db', 'r')
        feedback_dict = db.get('Feedback', {})
    except KeyError:
        print("KeyError: 'Feedback' not found in the shelve database.")

    db.close()

    return render_template('Dashboard/RetrieveFeedback.html', feedback_dict=feedback_dict)

@app.route('/UpdateFeedback/<int:id>/', methods=['GET', 'POST'])
def update_feedback(id):

    update_feedback_form = CreateFeedbackForm(request.form)
    if request.method == 'POST' and update_feedback_form.validate():
        feedback_dict = {}
        db = shelve.open('feedback.db', 'w')
        feedback_dict = db['Feedback']


        feedback = feedback_dict.get(id)
        feedback.set_first_name(update_feedback_form.first_name.data)
        feedback.set_last_name(update_feedback_form.last_name.data)
        feedback.set_email(update_feedback_form.email.data)
        feedback.set_phone_number(update_feedback_form.phone_number.data)
        feedback.set_gender(update_feedback_form.gender.data)
        feedback.set_age(update_feedback_form.age.data)
        feedback.set_date_made(update_feedback_form.date_made.data)
        feedback.set_remarks(update_feedback_form.remarks.data)

        db['Feedback'] = feedback_dict
        db.close()
        return redirect(url_for('retrieve_feedback'))


    else:
        feedback_dict = {}
        db = shelve.open('feedback.db', 'r')
        feedback_dict = db['Feedback']
        db.close()

        feedback = feedback_dict.get(id)
        update_feedback_form.first_name.data = feedback.get_first_name()
        update_feedback_form.last_name.data = feedback.get_last_name()
        update_feedback_form.email.data = feedback.get_email()
        update_feedback_form.phone_number.data = feedback.get_phone_number()
        update_feedback_form.gender.data = feedback.get_gender()
        update_feedback_form.age.data = feedback.get_age()
        update_feedback_form.date_made.data = feedback.get_date_made()
        update_feedback_form.remarks.data = feedback.get_remarks()

        return render_template('Dashboard/UpdateFeedback.html', form=update_feedback_form)

@app.route('/DeleteFeedback/<int:id>', methods=['POST'])
def delete_Feedback(id):
    feedback_dict = {}
    db = shelve.open('feedback.db', 'w')
    feedback_dict = db['Feedback']

    feedback_dict.pop(id)

    db['Feedback'] = feedback_dict
    db.close()

    return redirect(url_for('retrieve_feedback'))

@app.route('/Feedback_submission', methods=['POST'])
def feedback_submission():
    # Process form submission and get form data
    form_data = {
        'name': request.form.get('name'),
        'email': request.form.get('email'),
        # Add more fields as needed
    }

# test
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587  # or the appropriate port for your mail server
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'orangecrussh1@gmail.com'
app.config['MAIL_PASSWORD'] = 'jide vemz kfmu imor'
app.config['MAIL_DEFAULT_SENDER'] = 'orangecrussh1@gmail.com'

mail = Mail(app)

def send_invoice_email(charity):
    subject = 'Invoice for Charity Application'
    recipients = [charity.get_email()]  # Assuming the email is stored in the Charity object

    message = render_template('email/invoice.html', charity=charity)
    msg = Message(subject, recipients=recipients, html=message)

    # Send the email
    mail.send(msg)
def send_invoice_email(feedback):
    subject = 'Invoice for Charity Application'
    recipients = [feedback.get_email()]  # Assuming the email is stored in the Charity object

    message = render_template('email/invoice_feedback.html', feedback=feedback)
    msg = Message(subject, recipients=recipients, html=message)

    # Send the email
    mail.send(msg)

@app.route('/CustomerSignup', methods=['GET', 'POST'])
def create_customer():
    create_customer_form = CreateCustomerForm(request.form)

    if request.method == 'POST' and create_customer_form.validate():
        email_to_check = create_customer_form.email.data.lower()

        try:
            with shelve.open('customer.db', 'c') as customer_db, shelve.open('admin.db', 'r') as admin_db, shelve.open('staff.db', 'r') as staff_db:
                customers_dict = customer_db.get('Customers', {})
                existing_customer_data = next(
                    (customer_data for customer_data in customers_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_customer_data:
                    flash('Email already in use. Please use a different email address.', 'error')
                    return redirect(url_for('create_customer'))

                staff_dict = staff_db.get('StaffMembers', {})
                existing_staff_data = next(
                    (customer_data for customer_data in staff_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_staff_data:
                    flash('Email already in use by staff. Please use a different email address.', 'error')
                    return redirect(url_for('create_customer'))

                admin_dict = admin_db.get('Admins', {})
                existing_admin_data = next(
                    (customer_data for customer_data in admin_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_admin_data:
                    flash('Email already in use by admin. Please use a different email address.', 'error')
                    return redirect(url_for('create_customer'))

                customer = Customer(
                    create_customer_form.first_name.data,
                    create_customer_form.last_name.data,
                    create_customer_form.email.data,
                    create_customer_form.phone_number.data,
                    create_customer_form.password.data,
                    create_customer_form.gender.data,
                    create_customer_form.age.data,
                    create_customer_form.role.data
                )
                customers_dict[customer.get_user_id()] = customer
                customer_db['Customers'] = customers_dict

                flash('User created and added to the customer database successfully.', 'success')

                create_customer_form.email.data = ''
                create_customer_form.first_name.data = ''
                create_customer_form.last_name.data = ''
                create_customer_form.phone_number.data = ''
                create_customer_form.password.data = ''
                create_customer_form.gender.data = ''
                create_customer_form.age.data = ""
                create_customer_form.role.data = ''

        except Exception as e:
            flash(f'Error creating customer account: {str(e)}', 'error')

    return render_template('Website/CreateNewAccount.html', form=create_customer_form)


@app.route('/RetrieveCustomer', methods=['GET'])
def retrieve_customers():
    try:
        with shelve.open('customer.db', 'r') as db:
            customers_dict = db.get('Customers', {})
            customers_list = list(customers_dict.values())
            return render_template('Dashboard/RetrieveCustomer.html', count=len(customers_list), customers_list=customers_list)
    except dbm.error as e:
        app.logger.warning(f"Database error: {str(e)}")

        edit_order_form = EditOrderInputForm()

        error = None

        if request.method == 'POST' and edit_order_form.validate_on_submit():
            order_id_to_edit = edit_order_form.order_id_to_edit.data

            customer_to_edit = None
            order_to_edit = None

            for user_id, customer_data in customers_dict.items():
                for order in customer_data._orders:
                    if order['order_id'] == order_id_to_edit:
                        customer_to_edit = customer_data
                        order_to_edit = order
                        break

            if customer_to_edit and order_to_edit:
                return redirect(url_for('edit_order', order_id=order_id_to_edit))
            else:
                print("Error")
                error = 'Invalid Order ID. Please try again.'

        return render_template('Dashboard/RetrieveCustomer.html', count=0, customers_list=[], edit_order_form=edit_order_form, error=error)


@app.route('/Profile')
def view_profile():
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    customer = get_user_by_id(user_id, user_role)

    if customer:
        return render_template('Website/Profile.html', customer=customer)
    else:
        return render_template('Website/index.html')


@app.route('/EditProfile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')

    update_customer_form = CreateCustomerForm(request.form)
    customers_dict = {}

    try:
        if request.method == 'POST' and update_customer_form.validate():
            with shelve.open('customer.db', 'c') as db:
                customers_dict = db.get('Customers', {})
                customer = customers_dict.get(user_id)

                if customer:
                    # Update customer information
                    customer.set_first_name(update_customer_form.first_name.data)
                    customer.set_last_name(update_customer_form.last_name.data)
                    customer.set_phone_number(update_customer_form.phone_number.data)
                    customer.set_gender(update_customer_form.gender.data)
                    customer.set_age(update_customer_form.age.data)

                    db['Customers'] = customers_dict
                    session['customer_updated'] = customer.get_user_id()

                    # Flash message for successful update
                    flash('Profile updated successfully!', 'success')

                    return redirect(url_for('view_profile'))
                else:
                    flash(f"Customer with ID {user_id} not found.")
    except Exception as e:
        flash(f"Error updating customer: {e}")
    finally:
        if 'db' in locals():
            db.close()

    customers_dict = {}
    db = shelve.open('customer.db', 'r')
    customers_dict = db['Customers']
    db.close()

    customer = customers_dict.get(user_id)

    if customer:
        update_customer_form.first_name.data = customer.get_first_name()
        update_customer_form.last_name.data = customer.get_last_name()
        update_customer_form.email.data = customer.get_email()
        update_customer_form.phone_number.data = customer.get_phone_number()
        update_customer_form.password.data = customer.get_password()
        update_customer_form.gender.data = customer.get_gender()
        update_customer_form.age.data = customer.get_age()

        session['customer_updated'] = customer.get_email()
        return render_template('Website/EditProfile.html', form=update_customer_form, customer=customer)
    else:
        flash(f"Customer with ID {user_id} not found.")
        return redirect(url_for('retrieve_customers'))

@app.route('/ViewCustomer', methods=['GET'])
def view_customers():
    try:
        with shelve.open('customer.db', 'r') as db:
            customers_dict = db.get('Customers', {})
            customers_list = list(customers_dict.values())
            return render_template('Dashboard/ViewCustomer.html', count=len(customers_list), customers_list=customers_list)
    except dbm.error as e:
        app.logger.warning(f"Database error: {str(e)}")

        edit_order_form = EditOrderInputForm()

        error = None

        if request.method == 'POST' and edit_order_form.validate_on_submit():
            order_id_to_edit = edit_order_form.order_id_to_edit.data

            customer_to_edit = None
            order_to_edit = None

            for user_id, customer_data in customers_dict.items():
                for order in customer_data._orders:
                    if order['order_id'] == order_id_to_edit:
                        customer_to_edit = customer_data
                        order_to_edit = order
                        break

            if customer_to_edit and order_to_edit:
                return redirect(url_for('edit_order', order_id=order_id_to_edit))
            else:
                print("Error")
                error = 'Invalid Order ID. Please try again.'

        return render_template('Dashboard/ViewCustomer.html', count=0, customers_list=[], edit_order_form=edit_order_form, error=error)

@app.route('/UpdateCustomer/<int:id>/', methods=['GET', 'POST'])
def update_customer(id):
    update_customer_form = CreateCustomerForm(request.form)

    try:
        if request.method == 'POST' and update_customer_form.validate():
            customers_dict = {}
            db = shelve.open('customer.db', 'c')

            customers_dict = db['Customers']
            customer = customers_dict.get(id)

            if customer:
                customer.set_first_name(update_customer_form.first_name.data)
                customer.set_last_name(update_customer_form.last_name.data)
                customer.set_email(update_customer_form.email.data)
                customer.set_phone_number(update_customer_form.phone_number.data)
                customer.set_password(update_customer_form.password.data)
                customer.set_gender(update_customer_form.gender.data)
                customer.set_age(update_customer_form.age.data)

                db['Customers'] = customers_dict
                db.close()

                session['customer_updated'] = customer.get_user_id()
                return redirect(url_for('retrieve_customers'))
            else:
                flash(f"Customer with ID {id} not found.")
    except Exception as e:
        flash(f"Error updating customer: {e}")
    finally:
        if 'db' in locals():
            db.close()

    customers_dict = {}
    db = shelve.open('customer.db', 'r')
    customers_dict = db['Customers']
    db.close()

    customer = customers_dict.get(id)

    if customer:
        update_customer_form.first_name.data = customer.get_first_name()
        update_customer_form.last_name.data = customer.get_last_name()
        update_customer_form.email.data = customer.get_email()
        update_customer_form.phone_number.data = customer.get_phone_number()
        update_customer_form.password.data = customer.get_password()
        update_customer_form.gender.data = customer.get_gender()
        update_customer_form.age.data = customer.get_age()

        session['customer_updated'] = customer.get_email()
        return render_template('Dashboard/UpdateCustomer.html', form=update_customer_form)
    else:
        flash(f"Customer with ID {id} not found.")
        return redirect(url_for('retrieve_customers'))

@app.route('/reservation')
def reservation():
    return render_template('/Website/reservation.html')

@app.route('/DeleteCustomer/<int:id>', methods=['POST'])
def delete_customer(id):
    customers_dict = {}
    db = shelve.open('customer.db', 'w')
    customers_dict = db['Customers']

    if id in customers_dict:
        customers_dict.pop(id)
        db['Customers'] = customers_dict
        db.close()
        session['customer_deleted'] = id
        flash(f'Customer with ID {id} has been deleted successfully.', 'info')
    else:
        flash(f'Customer with ID {id} not found.', 'error')

    return redirect(url_for('retrieve_customers'))

@app.route('/StaffSignup', methods=['GET', 'POST'])
def create_staff():
    create_staff_form = CreateStaffForm(request.form)

    if request.method == 'POST' and create_staff_form.validate():
        email_to_check = create_staff_form.email.data.lower()

        try:
            with shelve.open('staff.db', 'c') as staff_db, shelve.open('admin.db', 'r') as admin_db, shelve.open('customer.db', 'r') as customer_db:
                staff_dict = staff_db.get('StaffMembers', {})
                existing_staff_data = next(
                    (customer_data for customer_data in staff_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_staff_data:
                    flash('Email already in use. Please use a different email address.', 'error')
                    return redirect(url_for('create_staff'))

                customer_dict = customer_db.get('Customers', {})
                existing_customer_data = next(
                    (customer_data for customer_data in customer_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_customer_data:
                    flash('Email already in use by customer. Please use a different email address.', 'error')
                    return redirect(url_for('create_staff'))

                admin_dict = admin_db.get('Admins', {})
                existing_admin_data = next(
                    (customer_data for customer_data in admin_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_admin_data:
                    flash('Email already in use by admin. Please use a different email address.', 'error')
                    return redirect(url_for('create_staff'))

                staff_member = Staff.Staff(
                    create_staff_form.first_name.data,
                    create_staff_form.last_name.data,
                    create_staff_form.email.data,
                    create_staff_form.phone_number.data,
                    create_staff_form.password.data,
                    create_staff_form.gender.data,
                    create_staff_form.age.data,
                    create_staff_form.role.data,
                    create_staff_form.position.data,
                    create_staff_form.address.data
                )
                staff_dict[staff_member.get_user_id()] = staff_member
                staff_db['StaffMembers'] = staff_dict

                flash('Staff member created and added to the staff database successfully.', 'success')

                create_staff_form.email.data = ''
                create_staff_form.first_name.data = ''
                create_staff_form.last_name.data = ''
                create_staff_form.phone_number.data = ''
                create_staff_form.password.data = ''
                create_staff_form.gender.data = ''
                create_staff_form.age.data = ""
                create_staff_form.role.data = ''
                create_staff_form.position.data = ''
                create_staff_form.address.data = ''

        except Exception as e:
            flash(f'Error creating staff member account: {str(e)}', 'error')

    return render_template('Dashboard/CreateNewStaffAccount.html', form=create_staff_form)

@app.route('/RetrieveStaff', methods=['GET'])
def retrieve_staffs():
    try:
        with shelve.open('staff.db', 'r') as db:
            staff_dict = db.get('StaffMembers', {})
            staff_list = list(staff_dict.values())
            return render_template('Dashboard/RetrieveStaff.html', count=len(staff_list), staff_list=staff_list)
    except dbm.error as e:
        app.logger.warning(f"Database error: {str(e)}")
        return render_template('Dashboard/RetrieveStaff.html', count=0, staff_list=[])

@app.route('/ViewStaff', methods=['GET'])
def view_staffs():
    try:
        with shelve.open('staff.db', 'r') as db:
            staff_dict = db.get('StaffMembers', {})
            staff_list = list(staff_dict.values())
            return render_template('Dashboard/ViewStaff.html', count=len(staff_list), staff_list=staff_list)
    except dbm.error as e:
        app.logger.warning(f"Database error: {str(e)}")
        return render_template('Dashboard/ViewStaff.html', count=0, staff_list=[])

@app.route('/UpdateStaff/<int:id>/', methods=['GET', 'POST'])
def update_staff(id):
    update_staff_form = CreateStaffForm(request.form)

    try:
        if request.method == 'POST' and update_staff_form.validate():
            staff_dict = {}
            db = shelve.open('staff.db', 'c')

            staff_dict = db['StaffMembers']
            staff = staff_dict.get(id)

            if staff:
                staff = staff_dict.get(id)
                staff.set_first_name(update_staff_form.first_name.data)
                staff.set_last_name(update_staff_form.last_name.data)
                staff.set_email(update_staff_form.email.data)
                staff.set_phone_number(update_staff_form.phone_number.data)
                staff.set_password(update_staff_form.password.data)
                staff.set_gender(update_staff_form.gender.data)
                staff.set_age(update_staff_form.age.data)
                staff.set_position(update_staff_form.position.data)
                staff.set_address(update_staff_form.address.data)

                db['StaffMembers'] = staff_dict
                db.close()

                session['customer_updated'] = staff.get_user_id()
                return redirect(url_for('retrieve_staffs'))
            else:
                flash(f"Staff with ID {id} not found.")
    except Exception as e:
        flash(f"Error updating staff: {e}")
    finally:
        if 'db' in locals():
            db.close()

    staff_dict = {}
    db = shelve.open('staff.db', 'r')
    staff_dict = db['StaffMembers']
    db.close()

    staff = staff_dict.get(id)

    if staff:
        staff = staff_dict.get(id)
        update_staff_form.first_name.data = staff.get_first_name()
        update_staff_form.last_name.data = staff.get_last_name()
        update_staff_form.email.data = staff.get_email()
        update_staff_form.phone_number.data = staff.get_phone_number()
        update_staff_form.password.data = staff.get_password()
        update_staff_form.gender.data = staff.get_gender()
        update_staff_form.age.data = staff.get_age()
        update_staff_form.position.data = staff.get_position()
        update_staff_form.address.data = staff.get_address()

        session['staff_updated'] = staff.get_email()
        return render_template('Dashboard/UpdateStaff.html', form=update_staff_form)
    else:
        flash(f"Staff with ID {id} not found.")
        return redirect(url_for('retrieve_staffs'))

@app.route('/DeleteStaff/<int:id>', methods=['POST'])
def delete_staff(id):
    staff_dict = {}
    db = shelve.open('staff.db', 'w')
    staff_dict = db['StaffMembers']

    if id in staff_dict:
        staff_dict.pop(id)
        db['StaffMembers'] = staff_dict
        db.close()
        session['staff_deleted'] = id
        flash(f'Staff with ID {id} has been deleted successfully.', 'info')
    else:
        flash(f'Staff with ID {id} not found.', 'error')

    return redirect(url_for('retrieve_staffs'))

@app.route('/AdminSignup', methods=['GET', 'POST'])
def create_admin():
    create_admin_form = CreateAdminForm(request.form)

    if request.method == 'POST' and create_admin_form.validate():
        email_to_check = create_admin_form.email.data.lower()

        try:
            with shelve.open('admin.db', 'c') as admin_db, shelve.open('customer.db', 'r') as customer_db, shelve.open('staff.db', 'r') as staff_db:
                admin_dict = admin_db.get('Admins', {})
                existing_admin_data = next(
                    (customer_data for customer_data in admin_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_admin_data:
                    flash('Email already in use. Please use a different email address.', 'error')
                    return redirect(url_for('create_admin'))

                customers_dict = customer_db.get('Customers', {})
                existing_customer_data = next(
                    (customer_data for customer_data in customers_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_customer_data:
                    flash('Email already in use by customer. Please use a different email address.', 'error')
                    return redirect(url_for('create_admin'))

                staff_dict = staff_db.get('StaffMembers', {})
                existing_staff_data = next(
                    (customer_data for customer_data in staff_dict.values() if customer_data.get_email().lower() == email_to_check),
                    None)
                if existing_staff_data:
                    flash('Email already in use by staff. Please use a different email address.', 'error')
                    return redirect(url_for('create_admin'))

                admin_member = Admin.Admin(
                    create_admin_form.first_name.data,
                    create_admin_form.last_name.data,
                    create_admin_form.email.data,
                    create_admin_form.phone_number.data,
                    create_admin_form.password.data,
                    create_admin_form.gender.data,
                    create_admin_form.age.data,
                    create_admin_form.role.data,
                    create_admin_form.address.data
                )
                admin_dict[admin_member.get_user_id()] = admin_member
                admin_db['Admins'] = admin_dict

                flash('Admin member created and added to the admin database successfully.', 'success')

                create_admin_form.email.data = ''
                create_admin_form.first_name.data = ''
                create_admin_form.last_name.data = ''
                create_admin_form.phone_number.data = ''
                create_admin_form.password.data = ''
                create_admin_form.gender.data = ''
                create_admin_form.age.data = ""
                create_admin_form.role.data = ''
                create_admin_form.address.data = ''

        except Exception as e:
            flash(f'Error creating admin member account: {str(e)}', 'error')

    return render_template('Dashboard/CreateNewAdminAccount.html', form=create_admin_form)

@app.route('/RetrieveAdmin', methods=['GET'])
def retrieve_admins():
    try:
        with shelve.open('admin.db', 'r') as db:
            admin_dict = db.get('Admins', {})
            admin_list = list(admin_dict.values())
            return render_template('Dashboard/RetrieveAdmin.html', count=len(admin_list), admin_list=admin_list)
    except dbm.error as e:
        app.logger.warning(f"Database error: {str(e)}")
        return render_template('Dashboard/RetrieveAdmin.html', count=0, admin_list=[])


@app.route('/UpdateAdmin/<int:id>/', methods=['GET', 'POST'])
def update_admin(id):
    update_admin_form = CreateAdminForm(request.form)

    try:
        if request.method == 'POST' and update_admin_form.validate():
            admin_dict = {}
            db = shelve.open('admin.db', 'c')

            admin_dict = db['Admins']
            admin = admin_dict.get(id)

            if admin:
                admin = admin_dict.get(id)
                admin.set_first_name(update_admin_form.first_name.data)
                admin.set_last_name(update_admin_form.last_name.data)
                admin.set_email(update_admin_form.email.data)
                admin.set_phone_number(update_admin_form.phone_number.data)
                admin.set_password(update_admin_form.password.data)
                admin.set_gender(update_admin_form.gender.data)
                admin.set_age(update_admin_form.age.data)
                admin.set_address(update_admin_form.address.data)

                db['Admins'] = admin_dict
                db.close()

                session['customer_updated'] = admin.get_user_id()
                return redirect(url_for('retrieve_admins'))
            else:
                flash(f"Admin with ID {id} not found.")
    except Exception as e:
        flash(f"Error updating admin: {e}")
    finally:
        if 'db' in locals():
            db.close()

    admin_dict = {}
    db = shelve.open('admin.db', 'r')
    admin_dict = db['Admins']
    db.close()

    admin = admin_dict.get(id)

    if admin:
        admin = admin_dict.get(id)
        update_admin_form.first_name.data = admin.get_first_name()
        update_admin_form.last_name.data = admin.get_last_name()
        update_admin_form.email.data = admin.get_email()
        update_admin_form.phone_number.data = admin.get_phone_number()
        update_admin_form.password.data = admin.get_password()
        update_admin_form.gender.data = admin.get_gender()
        update_admin_form.age.data = admin.get_age()
        update_admin_form.address.data = admin.get_address()

        session['admin_updated'] = admin.get_email()
        return render_template('Dashboard/UpdateAdmin.html', form=update_admin_form)
    else:
        flash(f"Admin with ID {id} not found.")
        return redirect(url_for('retrieve_admins'))

@app.route('/DeleteAdmin/<int:id>', methods=['POST'])
def delete_admin(id):
    admin_dict = {}
    db = shelve.open('admin.db', 'w')
    admin_dict = db['Admins']

    if id in admin_dict:
        admin_dict.pop(id)
        db['Admins'] = admin_dict
        db.close()
        session['admin_deleted'] = id
        flash(f'Admin with ID {id} has been deleted successfully.', 'info')
    else:
        flash(f'Admin with ID {id} not found.', 'error')

    return redirect(url_for('retrieve_admins'))

@app.route('/Book', methods=['GET', 'POST'])
def create_book():
    create_book_form = CreateBookForm(request.form)

    if 'user_id' not in session:
        flash('Please log in to book a seat.', 'error')
        return redirect(url_for('login'))

    # If the user is logged in, pre-fill the form fields
    if session.get('user_id') and session.get('user_role'):
        user = get_user_by_id(session.get('user_id'), session.get('user_role'))
        if user:
            create_book_form.first_name.data = user.get_first_name()
            create_book_form.last_name.data = user.get_last_name()
            create_book_form.email.data = user.get_email()
            create_book_form.phone_number.data = getattr(user, 'get_phone_number', '')()
            create_book_form.password.data = user.get_password()
            create_book_form.gender.data = user.get_gender()
            create_book_form.age.data = user.get_age()

    # Handle the POST request when the form is submitted
    if request.method == 'POST' and create_book_form.validate():
        book_dict = {}
        db = shelve.open('book.db', 'c')

        try:
            book_dict = db['Book']
        except:
            print("Error in retrieving Book from book.db")

        # Get the current date and time
        current_date = datetime.now()

        # Format the date as 'Y-M-D'
        formatted_date = current_date.strftime('%Y-%m-%d')

        # Get user ID from session
        user_id = session.get('user_id')

        # Check if user is logged in
        if not user_id:
            flash('Please log in before making a booking.', 'error')
            db.close()
            return redirect(url_for('login'))

        user_role = session.get('user_role', '')

        # Create a Book instance and store it in the book dictionary
        book = Book.Book(
            create_book_form.first_name.data,
            create_book_form.last_name.data,
            create_book_form.email.data,
            create_book_form.phone_number.data,
            create_book_form.password.data,
            create_book_form.gender.data,
            create_book_form.age.data,
            user_role,
            create_book_form.party_size.data,
            formatted_date,
            create_book_form.time_slot.data,
            create_book_form.comments.data,
            create_book_form.booking_status.data
        )
        book_dict[book.get_book_id()] = book
        db['Book'] = book_dict

        db.close()

        flash('Book submitted successfully. Thank you!', 'success')

        return redirect(url_for('home'))

    # Render the book form template
    return render_template('Website/Book.html', form=create_book_form)
@app.route('/RetrieveBook')
def retrieve_book():
    book_dict = {}
    db = shelve.open('book.db', 'r')
    book_dict = db.get('Book', {})
    db.close()

    for book in book_dict.values():
        book.update_booking_status()

    book_list = list(book_dict.values())

    current_time = datetime.now()

    return render_template('Dashboard/RetrieveBook.html', count=len(book_list), book_list=book_list, current_time=current_time)

@app.route('/UpdateBook/<int:id>/', methods=['GET', 'POST'])
def update_book(id):
    update_book_form = CreateBookForm(request.form)
    if request.method == 'POST' and update_book_form.validate():
        book_dict = {}
        db = shelve.open('book.db', 'w')
        book_dict = db['Book']

        book = book_dict.get(id)
        book.set_first_name(update_book_form.first_name.data)
        book.set_last_name(update_book_form.last_name.data)
        book.set_email(update_book_form.email.data)
        book.set_phone_number(update_book_form.phone_number.data)
        book.set_party_size(update_book_form.party_size.data)
        book.set_date(update_book_form.date.data)
        book.set_time_slot(update_book_form.time_slot.data)
        book.set_comments(update_book_form.comments.data)
        book.set_booking_status(update_book_form.booking_status.data)

        db['Book'] = book_dict
        db.close()

        return redirect(url_for('retrieve_book'))
    else:
        book_dict = {}
        db = shelve.open('book.db', 'r')
        book_dict = db['Book']
        db.close()

        book = book_dict.get(id)
        update_book_form.first_name.data = book.get_first_name()
        update_book_form.last_name.data = book.get_last_name()
        update_book_form.email.data = book.get_email()
        update_book_form.phone_number.data = book.get_phone_number()
        update_book_form.party_size.data = book.get_party_size()
        update_book_form.date.data = book.get_date()
        update_book_form.time_slot.data = book.get_time_slot()
        update_book_form.comments.data = book.get_comments()
        update_book_form.booking_status.data = book.get_booking_status()

        return render_template('Dashboard/UpdateBook.html', form=update_book_form)

@app.route('/DeleteBook/<int:id>', methods=['POST'])
def delete_book(id):
    book_dict = {}
    db = shelve.open('book.db', 'w')
    book_dict = db['Book']

    book_dict.pop(id)

    db['Book'] = book_dict
    db.close()

    return redirect(url_for('retrieve_book'))


@app.route('/Dashboard')
def dashboard():
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    user = get_user_by_id(user_id, user_role)

    if user:
        user_first_name = user.get_first_name()
        user_last_name = user.get_last_name()
        return render_template('Dashboard/index.html', user_first_name=user_first_name, user_last_name=user_last_name)
    else:
        return render_template('Dashboard/index.html')



@app.route('/')
def home():
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    user = get_user_by_id(user_id, user_role)

    if user:
        user_first_name = user.get_first_name()
        user_last_name = user.get_last_name()
        return render_template('Website/index.html', user_first_name=user_first_name, user_last_name=user_last_name)
    else:
        return render_template('Website/index.html')

def get_user_by_id(user_id, user_role):
    if user_role == 'customer':
        with shelve.open('customer.db', 'r') as customer_db:
            customers_dict = customer_db.get('Customers', {})
            return customers_dict.get(user_id)
    elif user_role == 'staff':
        with shelve.open('staff.db', 'r') as staff_db:
            staff_dict = staff_db.get('StaffMembers', {})
            return staff_dict.get(user_id)
    elif user_role == 'admin':
        with shelve.open('admin.db', 'r') as admin_db:
            admin_dict = admin_db.get('Admins', {})
            return admin_dict.get(user_id)
    else:
        return None

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def reset_customer_orders():
    with shelve.open('customer.db', writeback=True) as db:
        customers = db.get('Customers', {})
        for user_id, customer_data in customers.items():
            # Create or update the order history list
            if '_order_history' not in customer_data.__dict__:
                customer_data._order_history = []

            # Check if '_orders' attribute exists before accessing it
            if hasattr(customer_data, '_orders'):
                customer_data._order_history.extend(customer_data._orders)

                # Reset order details
                customer_data._orders = []
                customer_data.__dict__.update({'_orders': []})

def reset_cart():
    with shelve.open('cart_db') as db:
        # Preserve the existing order_id_counter
        order_id_counter = db.get('order_id_counter', 0)

        # Reset the 'cart' key
        db['cart'] = {}

        # Restore the order_id_counter
        db['order_id_counter'] = order_id_counter


@app.before_request
def before_request():
    # Check if it's the first request
    if not getattr(app, 'initialized', False):
        # Reset customer orders before the first request is handled
        reset_customer_orders()
        with shelve.open('cart_db') as db:
            Customer.order_id_counter = db.get('order_id_counter', 0)
        # Set the initialized flag to True to indicate that initialization has occurred
        app.initialized = True

@app.route('/order_history/<user_id>')
def order_history(user_id):
    with shelve.open('customer.db', 'r') as db:
        customers = db.get('Customers', {})
        customer_data = customers.get(int(user_id))

        if customer_data:
            order_history = customer_data._order_history

            return render_template('Dashboard/order_history.html', user_id=user_id, order_history=order_history)
        else:
            error = 'User not found.'
            return render_template('Website/error.html', error=error)

@app.route('/ViewOrder')
def view_order_history():
    user_id = session.get('user_id')
    with shelve.open('customer.db', 'r') as db:
        customers = db.get('Customers', {})
        customer_data = customers.get(int(user_id))

        if customer_data:
            order_history = customer_data._order_history

            return render_template('Website/ViewOrder.html', user_id=user_id, order_history=order_history)
        else:
            error = 'User not found.'
            return render_template('Website/error.html', error=error)

def init_db():
    with shelve.open('cart_db') as db:
        # Initialize 'cart' if not already present
        db.setdefault('cart', {})

        # Initialize 'menu_items' if not already present
        db.setdefault('menu_items', {})

if 'cart_db' not in globals():
    init_db()

@app.route('/AboutUs')
def about_us():
    return render_template('Website/AboutUs.html')


@app.route('/redeem_points', methods=['POST'])
def redeem_points():
    if 'user_id' in session:
        user_id = session['user_id']
        loyalty_points = int(request.form['loyalty_points'])

        with shelve.open('customer.db', 'c') as db:
            customers_dict = db.get('Customers', {})
            redeem = customers_dict.get_loyalty() - loyalty_points
            customer = customers_dict.get(user_id)
            if customer:
                customer.set_loyalty(redeem)
                customers_dict[user_id] = customer
                db['Customers'] = customers_dict
                session['customer_updated'] = customer.get_user_id()

        flash(f'{loyalty_points} loyalty points redeemed successfully!', 'success')
    return redirect(url_for('menu'))  # Redirect to the menu page after redeeming points


@app.route('/checkout_with_points_and_redeem/<user_id>', methods=['POST'])
def checkout_with_points_and_redeem(user_id):
    loyalty_points = int(request.form.get('loyalty_points', 0))

    if 'user_id' in session and session['user_id'] == user_id:
        with shelve.open('customer.db', 'c') as db:
            customers_dict = db.get('Customers', {})
            customer = customers_dict.get(user_id)

            if customer:
                available_points = customer.get_loyalty()

                if loyalty_points <= available_points:
                    # Calculate the updated loyalty points after redemption
                    updated_points = available_points - loyalty_points
                    customer.set_loyalty(updated_points)

                    # Update the customer's loyalty points in the database
                    customers_dict[user_id] = customer
                    db['Customers'] = customers_dict

                    # Flash a success message for loyalty points redemption
                    flash(f'{loyalty_points} loyalty points redeemed successfully!', 'success')

                else:
                    # Flash an error message if the user tries to redeem more points than available
                    flash('Not enough loyalty points for redemption!', 'error')

            else:
                # Flash an error message if the user is not found in the database
                flash('User not found!', 'error')

    # Redirect to the checkout page regardless of whether redemption was successful or not
    return redirect(url_for('checkout', user_id=user_id))


@app.route('/menu/', methods=['GET', 'POST'])
@app.route('/menu/<item>/', methods=['GET', 'POST'])
def menu(item=None):
    user_id = session.get('user_id')
    user_role = session.get('user_role')
    customer = get_user_by_id(user_id, user_role)

    with shelve.open('cart_db') as db:
        item_prices = db.get('menu_items', {})
        item_images = db.get('item_images', {})
        cart = db.get('cart', {})
        order_id_counter = db.get('order_id_counter', 0)

    total_price = calculate_total_price(cart, item_prices)

    return render_template('Website/menu.html', cart=cart, item_prices=item_prices, item_images=item_images, total_price=total_price, user_id=user_id, item=item, calculate_total_price=calculate_total_price, order_id_counter=order_id_counter, customer=customer)





@app.route('/admin_menu', methods=['GET', 'POST'])
@app.route('/admin_menu/<item>', methods=['GET', 'POST'])
def admin_menu(item=None):
    with shelve.open('cart_db') as db:
        item_prices = db.get('menu_items', {})
        item_images = db.get('item_images', {})
        cart = db.get('cart', {})
    total_price = calculate_total_price(cart, item_prices)
    return render_template('Dashboard/admin_menu.html', cart=cart, item_prices=item_prices, item_images=item_images ,total_price=total_price, item = item, calculate_total_price=calculate_total_price)

@app.route('/add_menu_item', methods=['GET', 'POST'])
def add_menu_item():
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_price = request.form['item_price']


        # Check if the post request has the file part
        if 'item_image' in request.files:
            file = request.files['item_image']
            if file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print("File Path:", file_path)  # Add this line for debugging
                file.save(file_path)
                # Store the filename or file path in your database along with other item details

                with shelve.open('cart_db', writeback=True) as db:
                    menu_items = db.get('menu_items', {})
                    menu_items[item_name] = float(item_price)
                    db['menu_items'] = menu_items

                    item_images = db.get('item_images', {})
                    item_images[item_name] = filename
                    db['item_images'] = item_images



    return render_template('Dashboard/add_menu_item.html')

@app.route('/delete_menu_item/<item>', methods=['POST'])
def delete_menu_item(item):
    with shelve.open('cart_db', writeback=True) as db:
        menu_items = db.get('menu_items', {})
        if item in menu_items:
            del menu_items[item]
            db['menu_items'] = menu_items

    return redirect(url_for('admin_menu', item = item))

@app.route('/add_to_cart/<item>/<user_id>', methods=['GET', 'POST'])
def add_to_cart(item, user_id):
    with shelve.open('cart_db') as db:
        cart = db.get('cart', {})
        # Get the user's current cart
        customer_cart = cart.get(int(user_id), {})
        # Increment the item count in the customer's cart
        customer_cart[item] = customer_cart.get(item, {'quantity': 0})
        customer_cart[item]['quantity'] += 1
        # Update the customer's cart in the overall cart
        cart[int(user_id)] = customer_cart
        # Update the overall cart in the database
        db['cart'] = cart

    return redirect(url_for('menu', item=item, user_id=user_id))

@app.route('/update_cart/<item>/<user_id>', methods=['POST'])
def update_cart(item, user_id):
    with shelve.open('cart_db') as db:
        cart = db.get('cart', {})
        customer_cart = cart.get(int(user_id), {})

        quantity_str = request.form.get('quantity', '')

        if quantity_str and quantity_str.isdigit():
            new_quantity = int(quantity_str)

            if 1 <= new_quantity <= 10:
                customer_cart[item]['quantity'] = new_quantity
                cart[int(user_id)] = customer_cart
                db['cart'] = cart
            else:
                flash('Quantity must be between 1 and 10.')
        else:
            flash('Invalid quantity value.')

    return redirect(url_for('menu', item=item, user_id=user_id))



@app.route('/remove_all_from_cart/<item>/<user_id>', methods=['POST'])
def remove_all_from_cart(item, user_id):
    with shelve.open('cart_db') as db:
        cart = db.get('cart', {})
        customer_cart = cart.get(int(user_id), {})
        customer_cart.pop(item, None)
        cart[int(user_id)] = customer_cart
        db['cart'] = cart
    return redirect(url_for('menu', item=item, user_id=user_id))

def calculate_total_price(customer_cart, item_prices):
    total_price = 0.0

    for user_id, customer_items in customer_cart.items():
        for item, item_data in customer_items.items():
            if isinstance(item_data, dict):
                quantity = item_data.get('quantity', 0)
                if item in item_prices:
                    item_price = item_prices[item]
                    total_price += quantity * item_price

    return total_price

def calculate_new_price(cart, item_prices):
    total_price = 0
    for item, quantity in cart.items():
        item_price = item_prices.get(item, 0)
        total_price += quantity * item_price
    return total_price


@app.route('/checkout/', methods=['GET', 'POST'])
def checkout():
    user_id = session.get('user_id')
    with shelve.open('cart_db', writeback=True) as db_cart, shelve.open('customer.db', writeback=True) as db:
        customer_data = db['Customers'].get(int(user_id))

        # Retrieve the cart and item prices
        cart = db_cart.get('cart', {})
        item_prices = db_cart.get('menu_items', {})

        # Check if the cart is empty
        if not any(cart.get(int(user_id), {}).values()):
            flash('Your cart is empty. Please add items to your cart before proceeding to checkout.')
            return redirect(url_for('menu', user_id=user_id))

        checkout_form = PaymentForm(request.form, obj=customer_data.payment_info if customer_data.payment_info else None)

        if request.method == 'POST' and checkout_form.validate():
            card_number = checkout_form.card_number.data
            cardholder_name = checkout_form.cardholder_name.data
            expiry_date = checkout_form.expiry_date.data
            cvc = checkout_form.cvc.data

            total_price = calculate_total_price(cart, item_prices)

            customer_data.update_payment_info(card_number, cardholder_name, expiry_date, cvc)

            customer_data.add_order(list(cart.get(int(user_id), {}).keys()), [data.get('quantity', 0) for data in cart.get(int(user_id), {}).values()], total_price)

            db['Customers'][int(user_id)] = customer_data

            # Clear the cart only after updating customer info and placing the order
            db_cart['cart'] = {}

            return redirect(url_for('order_confirmation', user_id=user_id))

        return render_template('Website/checkout.html', user_id=user_id, customer_data=customer_data, form=checkout_form)

@app.route('/order_confirmation/<user_id>')
def order_confirmation(user_id):
    # Open the shelve database containing customer details
    db = shelve.open('customer.db', 'r')
    try:
        customers = db['Customers']
    except KeyError:
        error = 'Invalid customer database.'
        db.close()
        return render_template('Website/error.html', error=error)

    # Retrieve the customer's data
    customer_data = customers.get(int(user_id))
    print(f"Order confirmation for {user_id}: {customer_data.orders}")

    reset_cart()

    db.close()

    return render_template('Website/order_confirmation.html', customer_data=customer_data)


@app.route('/save_payment_info/<user_id>', methods=['GET', 'POST'])
def save_payment_info(user_id):
    # Open the shelve database containing customer details
    db = shelve.open('customer.db', 'r')
    try:
        customers = db['Customers']
    except KeyError:
        error = 'Invalid customer database.'
        db.close()
        return render_template('Website/error.html', error=error)

    # Check if the customer with the provided user_id exists
    customer_data = customers.get(int(user_id))

    # Retrieve the saved payment information
    payment_info = getattr(customer_data, 'payment_info', {})

    db.close()

    return render_template('Website/save_payment_info.html', user_id=user_id, payment_info=payment_info)

@app.route('/update_payment_info/<user_id>', methods=['GET', 'POST'])
def update_payment_info(user_id):
    db = shelve.open('customer.db', 'w')
    customers = db.get('Customers', {})
    customer_data = customers.get(int(user_id))

    if customer_data is None:
        error = 'Customers not found.'
        db.close()
        return render_template('Website/error.html', error=error)

    payment_info = getattr(customer_data, 'payment_info')

    update_form = PaymentForm(obj=payment_info if payment_info else None)

    if request.method == 'POST':
        update_form = PaymentForm(request.form)
        if update_form.validate():
            customer_data.update_payment_info(
                update_form.card_number.data,
                update_form.cardholder_name.data,
                update_form.expiry_date.data,
                update_form.cvc.data
            )

            customers[int(user_id)] = customer_data
            db['Customers'] = customers
            db.close()

            return redirect(url_for('checkout', user_id=user_id))

    db.close()

    return render_template('Website/update_payment_info.html', user_id=user_id, form=update_form, customer_data=customer_data)

@app.route('/delete_payment_info/<user_id>', methods=['POST'])
def delete_payment_info(user_id):
    db = shelve.open('customer.db', 'w')
    customers = db.get('Customers', {})
    customer_data = customers.get(int(user_id))

    # Set payment_info to None to remove it
    customer_data.payment_info = None

    customers[int(user_id)] = customer_data
    db['Customers'] = customers
    db.close()

    return redirect(url_for('save_payment_info', user_id=user_id))

@app.route('/edit_order/<int:order_id>/', methods=['GET', 'POST'])
def edit_order(order_id):
    db = shelve.open('customer.db', 'r')
    try:
        customers = db['Customers']
        menu_items = shelve.open('cart_db', 'r')['menu_items']
    except KeyError:
        error = 'Invalid customer database.'
        db.close()
        return render_template('Website/error.html', error=error)

    order_to_edit = None

    for customer_data in customers.values():
        for order in customer_data._orders:
            if order['order_id'] == order_id:
                order_to_edit = order
                break

    db.close()

    if order_to_edit is None:
        return render_template('Website/error.html', error=f'Order with ID {order_id} not found.')

    edit_order_form = EditOrderMainForm()

    total_price = calculate_new_price(dict(zip(order_to_edit['item'], order_to_edit['quantity'])), menu_items)

    edit_order_form.total_price.data = total_price

    for quantity in order_to_edit['quantity']:
        edit_order_form.items.append_entry({'quantity': quantity})

    if request.method == 'POST':
        if edit_order_form.validate():
            # Extract 'quantity' values from the form data
            new_quantities = [int(request.form.get(f'items-{i}-quantity')) for i in range(len(order_to_edit['quantity']))]

            # Remove items with quantity 0 from the order
            order_to_edit['item'] = [item for i, item in enumerate(order_to_edit['item']) if new_quantities[i] > 0]
            order_to_edit['quantity'] = [quantity for quantity in new_quantities if quantity > 0]

            # Delete the order if there are no items left
            if not order_to_edit['item']:
                for user_id, customer_data in customers.items():
                    customer_data._orders = [order for order in customer_data._orders if order['order_id'] != order_id]

            # Calculate total price using the updated quantities and retrieved item prices
            total_price = calculate_new_price(dict(zip(order_to_edit['item'], order_to_edit['quantity'])), menu_items)
            order_to_edit['total_price'] = total_price

            # Update the total_price in the form
            edit_order_form.total_price.data = total_price

            with shelve.open('customer.db', 'w') as db_write:
                db_write['Customers'] = customers

            return redirect(url_for('retrieve_customers'))

    return render_template('Dashboard/edit_order.html', order=order_to_edit, form=edit_order_form)

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(debug=True)
