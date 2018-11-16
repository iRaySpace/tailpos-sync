# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe import _
from tailpos_sync.events import document_on_update, document_on_trash, document_on_save
import frappe
import uuid

class Discounts(Document):
    def autoname(self):
        if not self.id:
            self.id = 'Discount/' + str(uuid.uuid4())
        self.name = self.id

    def after_insert(self):

        if not self.from_couchdb:

            # Types
            types = {
                "Percentage": "percentage",
                "Fix Discount": "fixDiscount"
            }

            skeleton_doc = {
                "_id": self.id.replace("/backend", ""),
                "name": self.description,
                "value": self.value,
                "percentageType": types[self.type]
            }

            document_on_save(skeleton_doc, self.__dict__['doctype'])

    def validate(self):

        flags = self.__dict__['flags']

        if flags.in_insert:

            exists = frappe.db.sql("SELECT * FROM `tabDiscounts` WHERE description=%s", self.description)

            if len(exists) > 0:
                frappe.throw(_("Discount already exist!"))
        if self.date_updated == None:
            print("sdadasdasd")
            self.date_updated = self.modified
    def on_update(self):

        flags = self.__dict__['flags']

        # If only updates the document
        if not flags.in_insert:

            # This should be in Frappe
            if self.edit_type:

                types = {
                    "Percentage": "percentage",
                    "Fix Discount": "fixDiscount"
                }

                self.percentagetype = types[self.type]
                self.edit_type = 0

            # This should be in CouchDB
            else:

                types = {
                    "percentage": "Percentage",
                    "fixDiscount": "Fix Discount"
                }

                self.type = types[self.percentagetype]

            if not self.from_couchdb:
                document_on_update(self)

    def before_save(self):
        # self.syncstatus = "false"
        flags = self.__dict__['flags']

        if not flags.in_insert:

            if self.from_couchdb:
                types = {
                    "percentage": "Percentage",
                    "fixDiscount": "Fix Discount"
                }
                self.type = types[self.percentagetype]

    def on_trash(self):
        document_on_trash(self)