from flask import Blueprint, session, render_template, make_response, request, send_file, jsonify, redirect, flash
from .models import UploadedData, DataFormat, UsersData, db
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import zipfile
import io
from flask import request, send_file
import os
import re

# Create a blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    response = make_response(render_template('home.html'))
    # Set a cookie
    #response.set_cookie('example_cookie', 'cookie_value', max_age=60*60*24)  # Cookie lasts for 1 day
    response.set_cookie('Reza', 'Massah', max_age=6)  
    cookie_value = request.cookies.get('example_cookie')
    # print(cookie_value)
    return response

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/add')
def add():
    try:
        if session['username']:
            return render_template('add.html')
    except:
        return render_template('log_in.html', message="Please Log in first.")

@main.route('/remove')
def show_data():
    try:
        if session['username']:
            all_data = UploadedData.query.all()
            serialized_data = [{
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "file": 1 if item.file else 0
            } for item in all_data]
            return render_template('remove.html', data=serialized_data)
    except:
        return render_template('log_in.html', message="Please Log in first.")

@main.route('/contact')
def contact():
    return render_template('contact.html')

@main.route('/submit')
def submit():
    submitted_id = request.args.get('id', 'unknown')  
    return render_template('submit_data.html', id=submitted_id)

@main.route('/upload_data', methods=['POST'])
def upload_data():
    try:
        id = request.form.get('id')
        name = request.form.get('name')
        description = request.form.get('description')
        file = request.files.get('file')
        

        if not name:
            name = 'N/A'

        if not description:
            description = 'N/A'

        if not id or not name:
            return "ID and Name are required.", 400

        # Process the file if uploaded
        file_data = None
        if file and file.filename:
            file_data = file.read()

        print("Adding record to the database...")

        if file:
            _, file_format = os.path.splitext(file.filename)
            new_record_format = DataFormat(id=id, format=file_format)
            db.session.add(new_record_format)
            db.session.commit()
        else:
            new_record_format = DataFormat(id=id, format="N/A")
            db.session.add(new_record_format)  
            db.session.commit()  

        # Create a new record object
        new_record = UploadedData(id=id, name=name, description=description, file=file_data)

        # Add and commit to the database
        db.session.add(new_record)       

        try:
            db.session.commit()
            return "Data uploaded successfully!", 200
        except sqlite3.IntegrityError as e:  # Handle SQLite-specific errors
            db.session.rollback()
            print(f"SQLite IntegrityError: {e}")
            flash(f"SQLite IntegrityError: {e}", 'danger')
            return f"Integrity Error: {e}", 400
        except Exception as e:
            db.session.rollback()
            print(f"Error during commit: {e}")
            flash(f"Error during commit: {e}", 'danger')
            return f"Error during commit: {e}", 500

    except Exception as e:
        db.session.rollback()
        print(f"Error uploading data: {e}")
        flash(f"Error uploading data: {e}", 'danger')
        return f"Error uploading data: {e}", 500

@main.route('/delete-selected', methods=['POST'])
def delete_selected():
    selected_ids = request.form.getlist('selected_ids')

    if not selected_ids:
        return redirect('remove')

    try:
        for record_id in selected_ids:
            record = UploadedData.query.get(record_id)
            if record:
                db.session.delete(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    try:
        for record_id in selected_ids:
            record = DataFormat.query.get(record_id)
            if record:
                db.session.delete(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()

    return redirect('remove')

@main.route('/download-selected', methods=['POST'])
def download_selected():
    
    data = request.json
    selected_ids = data.get('selected_ids', [])

    if not selected_ids:
        return jsonify({"error": "No files selected"}), 400

    files = UploadedData.query.filter(UploadedData.id.in_(selected_ids)).all()
    formats = DataFormat.query.filter(DataFormat.id.in_(selected_ids)).all()

    if not files:
        return jsonify({"error": "No matching files found"}), 404

    # Create an in-memory ZIP file
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in files:
            if file.file:  # Ensure the file exists
                # Find the corresponding DataFormat object
                specific_format = next((f for f in formats if f.id == file.id), None)

                # Construct the filename
                if specific_format:
                    filename = f"{file.name}{specific_format.format}" if file.name else f"file_{file.id}.{specific_format.format}"
                else:
                    filename = file.name if file.name else f"file_{file.id}.bin"  # Fallback for missing format

                # Write the file to the ZIP
                zf.writestr(filename, file.file)

    memory_file.seek(0)

    # Return the ZIP file to the client
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='files.zip'
    )


@main.route('/thank_you', methods=['POST'])
def thank_you():
    return render_template('thank_you.html')


@main.route('/log_in', methods=['GET', 'POST'])
def log_in():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve the user from the database
        user = UsersData.query.filter_by(username=username).first()

        # Debugging: Check retrieved data
        print(f"Username: {username}")
        print(f"Password: {password}")
        print(f"Stored password hash: {user.password if user else 'User not found'}")

        # Check if the user exists
        if not user:
            return render_template('log_in.html', message="Invalid username or password.")

        # Verify the password
        if not check_password_hash(user.password, password):
            return render_template('log_in.html', message="Invalid username or password.")

        # Log the user in by setting the session
        session['username'] = user.username
        flash("Logged in successfully!", "success")
        return redirect('/')

    # Render the log-in page for GET requests
    return render_template('log_in.html')


@main.route('/sign_up')
def sign_up():
    return render_template('sign_up.html')


@main.route('/creating_account', methods=['GET', 'POST'])
def creating_account():
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        password = request.form.get('password')
        re_password = request.form.get('re_password')

        # Validation checks
        if len(username) < 6:
            return render_template('sign_up.html', message="Username must have at least 6 characters.")

        if password != re_password:
            return render_template('sign_up.html', message="Passwords do not match. Please try again.")

        if not any(char.isdigit() for char in password):
            return render_template('sign_up.html', message="Password must contain at least one number.")

        if not any(char.isupper() for char in password):
            return render_template('sign_up.html', message="Password must contain at least one uppercase letter.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return render_template('sign_up.html', message="Password must contain at least one special character (!@#$%^&*).")

        if len(password) < 8:
            return render_template('sign_up.html', message="Password must be at least 8 characters long.")

        # Check if username already exists
        existing_user = UsersData.query.filter_by(username=username).first()
        if existing_user:
            return render_template('sign_up.html', message="Username already exists. Please choose another.")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create new user instance
        new_user = UsersData(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=hashed_password
        )


        # Commit to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            # session['username'] = username  
            return redirect('/')
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")
            return render_template('sign_up.html', message="Something went wrong. Please try again.")

    return render_template('sign_up.html')

@main.context_processor
def inject_user():
    return {'username': session.get('username')}  # Automatically include 'username' in all templates

@main.route('/log_out')
def log_out():
    return render_template('Log_out.html')

@main.route('/remove_session', methods=['POST'])
def remove_session():
    session.clear()  # Clear session data
    flash('You have successfully logged out.', 'success')  # Optional: Provide feedback
    return redirect('/')  # Redirect to the home page
 
