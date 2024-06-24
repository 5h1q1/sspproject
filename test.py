@app.route('/AdminSignup', methods=['GET', 'POST'])
def create_admin():
    create_admin_form = CreateAdminForm(request.form)

    if request.method == 'POST' and create_admin_form.validate():
        email_to_check = create_admin_form.email.data.lower()

        try:
            with shelve.open('admin.db', 'c') as admin_db, shelve.open('customer.db', 'r') as customer_db:
                # Check if the email exists in the admin database
                admin_dict = admin_db.get('Admins', {})
                existing_admin_data = next(
                    (user_data for user_data in admin_dict.values() if user_data.get_email().lower() == email_to_check),
                    None)
                if existing_admin_data:
                    flash('Email already in use. Please use a different email address.', 'error')
                    return redirect(url_for('create_admin'))

                # Check if the email exists in the customer database
                customers_dict = customer_db.get('Customers', {})
                existing_customer_data = next(
                    (user_data for user_data in customers_dict.values() if user_data.get_email().lower() == email_to_check),
                    None)
                if existing_customer_data:
                    flash('Email already in use by customer. Please use a different email address.', 'error')
                    return redirect(url_for('create_admin'))

                # If the email is unique, proceed with creating the admin member
                admin_member = Admin.Admin(
                    create_admin_form.first_name.data,
                    create_admin_form.last_name.data,
                    create_admin_form.email.data,
                    create_admin_form.phone_number.data,
                    create_admin_form.password.data,
                    create_admin_form.gender.data,
                    create_admin_form.age.data,
                    create_admin_form.role.data,
                    create_admin_form.position.data,
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
                create_admin_form.position.data = ''
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
        # Database does not exist
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
                admin.set_position(update_admin_form.position.data)
                admin.set_address(update_admin_form.address.data)

                db['Admins'] = admin_dict
                db.close()

                session['customer_updated'] = admin.get_user_id()
                return redirect(url_for('retrieve_admins'))
            else:
                flash(f"Admin with ID {id} not found.")
        else:
            flash(f"Form validation failed: {update_admin_form.errors}")
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
        update_admin_form.position.data = admin.get_position()
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