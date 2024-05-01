from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import time
from bambu_connect import BambuClient, PrinterStatus
import pprint
from dataclasses import asdict
from .models import Note, Printer, File  # Import necessary models
from . import db  # Import the database instance
import json

# Create a Blueprint named 'views'
views = Blueprint('views', __name__)


# Route for the home page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')  # Gets the note from the HTML

        if len(note) < 1:
            flash('Note is too short!', category='error')  # Notify if note is too short
        else:
            # Create a new Note object and add it to the database
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')  # Notify that the note has been added successfully

    return render_template("home.html", user=current_user)


# Route for adding a new printer
@views.route('/printer', methods=['GET', 'POST'])
@login_required
def printer():
    if request.method == 'POST':
        name = request.form.get('Name')  # Gets the info from the HTML
        hostname = request.form.get('Hostname')
        access_code = request.form.get('AccessCode')
        serial = request.form.get('Serial')

        # Check if a printer with the same serial or name already exists
        printer = Printer.query.filter_by(serial=serial).first()
        if printer:
            flash('Printer already exists', category='error')
        printer = Printer.query.filter_by(name=name).first()
        if printer:
            flash('Printer name already in use', category='error')

        # Check if any field is too short
        elif len(name) < 1 or len(hostname) < 1 or len(access_code) < 1 or len(serial) < 1:
            flash('One or more fields are too short!', category='error')

        else:
            # Create a new Printer object and add it to the database
            new_printer = Printer(name=name, hostname=hostname,
                                  access_code=access_code, serial=serial, user_id=current_user.id)
            db.session.add(new_printer)
            db.session.commit()
            flash('Printer added!', category='success')  # Notify that the printer has been added successfully

    return render_template("printer.html", user=current_user)


# Route for deleting a printer
@views.route('/delete-printer', methods=['POST'])
@login_required
def delete_printer():
    # Load the JSON data sent from the frontend
    printer = json.loads(request.data)
    printerId = printer['printerId']
    printer = Printer.query.get(printerId)

    File.query.filter_by(printer_id=printerId).delete()
    db.session.commit()

    if printer:
        if printer.user_id == current_user.id:
            db.session.delete(printer)
            db.session.commit()
            flash('Printer removed!', category='error')  # Notify that the printer has been removed

    return jsonify({})


# Route for fetching data from a printer
@views.route('/fetch-data', methods=['POST'])
@login_required
def fetch_data():
    printer_id = request.json['printerId']
    printer = Printer.query.get(printer_id)

    if printer:
        hostname = printer.hostname
        access_code = printer.access_code
        serial = printer.serial

        # Create a BambuClient instance and fetch files from the printer
        bambu_client = BambuClient(hostname, access_code, serial)
        printer_files = bambu_client.get_files()

        # Delete existing files associated with the printer
        File.query.filter_by(printer_id=printer_id).delete()
        db.session.commit()

        # Add new files to the database
        for file in printer_files:
            new_file = File(filename=file, printer_id=printer_id)
            db.session.add(new_file)
            db.session.commit()
        flash('Files refreshed!', category='success')  # Notify that the files have been refreshed

    else:
        return jsonify({'error': 'Printer not found'}), 404  # Notify if the printer is not found
    return jsonify({})
