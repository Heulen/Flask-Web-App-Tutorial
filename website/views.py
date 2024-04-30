from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import time
from bambu_connect import BambuClient, PrinterStatus
import pprint
from dataclasses import asdict
from .models import Note, Printer
from . import db
import os
import json

views = Blueprint('views', __name__)

hostname = os.getenv('HOSTNAME', '192.168.1.84')
access_code = os.getenv('ACCESS_CODE', '25503239')
serial = os.getenv('SERIAL', '01P09A3A2700815')

bambu_client = BambuClient(hostname, access_code, serial)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        note = request.form.get('note')#Gets the note from the HTML 

        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
            db.session.add(new_note) #adding the note to the database 
            db.session.commit()
            flash('Note added!', category='success')
    
    printer_files = bambu_client.get_files()
    for file in printer_files:
            print(file)

    return render_template("home.html", user=current_user)

@views.route('/printer', methods=['GET', 'POST'])
@login_required
def printer():
    if request.method == 'POST': 
        name = request.form.get('Name')                 #Gets the info from the HTML
        hostname = request.form.get('Hostname')
        access_code = request.form.get('AccessCode')
        serial = request.form.get('Serial')


        if len(name) < 1 or len(hostname) < 1 or len(access_code) < 1 or len(serial) < 1:
            flash('One or more fields are too short!', category='error')

        else:
            new_printer = Printer(name=name, hostname=hostname, access_code=access_code, serial=serial, user_id=current_user.id)
            db.session.add(new_printer)
            db.session.commit()
            flash('Printer added!', category='success')

    
    printer_files = bambu_client.get_files()
    for file in printer_files:
            print(file)
            
    return render_template("printer.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
            flash('Note removed!', category='error')


    return jsonify({})
