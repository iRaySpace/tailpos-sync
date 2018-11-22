import string
import frappe
import requests
import urllib
from random import *
# from couchdb import client

server_url = "https://admin:qwerty@db.tailpos.com"
# server = client.Server(server_url)

def send_message(message, number):
    params = (
        ('apikey', 'xxxxxxxxxxx'),
        ('sendername', 'TAILPOS'),
        ('message', message),
        ('number', number)
    )
    path = 'https://semaphore.co/api/v4/messages?' + urllib.urlencode(params)
    requests.post(path)
    print 'Message Sent!'

def get_db_name(user):
    return frappe.db.sql("SELECT db_name FROM tabDevice WHERE user=%s", (user), as_dict=1)

def generate_password():
    characters = string.ascii_letters + string.punctuation + string.digits
    return "".join(choice(characters) for x in range(randint(12, 16)))

def add_role(doc, method):
    doc.add_roles('Subscriber')
    doc.save()

def document_on_save(doc, doctype_name):

    # Device
    device = get_db_name(frappe.session.user)

    if device:
        db_name = device[0].db_name
        db = server[db_name + '-' + doctype_name.lower()]
        db.save(doc)

def document_on_update(doc):

    # Device
    device = get_db_name(frappe.session.user)

    # Doctype
    doctype_name = doc.__dict__['doctype'].lower()

    # If there exists database
    if device:
        db_name = device[0].db_name
        db = server[db_name + '-' + doctype_name]

        # Document
        document = db.get(doc.id)

        if document:

            # Document key value
            document_kv = document.items()

            # _id, and _rev are in index 0 and 1
            for i in range(len(document_kv)):
                key = document_kv[i][0]
                if key == "name":
                    document[key] = doc.__dict__["description"]
                elif key == "_id" or key == "_rev":
                    continue
                else:
                    document[key] = doc.__dict__[key.lower()]

            # Save to the couchdb
            db.save(document)

def document_on_trash(doc):

    device = get_db_name(frappe.session.user)

    doctype_name = doc.__dict__['doctype'].lower()

    if device:
        db_name = device[0].db_name
        db = server[db_name + '-' + doctype_name]

        document = db.get(doc.id)

        if document:
            db.delete(document)
