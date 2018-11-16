# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe import _
from tailpos_sync.events import document_on_update, document_on_trash, document_on_save
import frappe
import uuid
import json

class Categories(Document):
    def autoname(self):
        if not self.id:
            self.id = 'Category/' + str(uuid.uuid4())
        self.name = self.id

    def after_insert(self):

        colors = {
            "Tomato": "tomato",
            "Fire Brick": "firebrick",
            "Blue": "blue",
            "Gray": "gray",
            "Green": "green",
            "Dark Orange": "darkorange",
            "Dark Magenta": "darkmagenta"
        }

        colorAndShape = [{ "color": colors[self.color], "shape": self.shape.lower() }]

        skeleton_doc = {
            "_id": self.id,
            "name": self.description,
            "colorAndShape": json.dumps(colorAndShape).replace(" ", "")
        }

        document_on_save(skeleton_doc, self.__dict__['doctype'])

    def validate(self):
        print("Category")
        print(self.date_updated == None)
        flags = self.__dict__['flags']

        if flags.in_insert:
            exists = frappe.db.sql("SELECT COUNT(*) as count FROM `tabCategories` WHERE description=%s", self.description, as_dict=1)[0]
            if exists.count:
                frappe.throw(_("Category already exist!"))
        if self.date_updated == None:
            print("Categorieees")
            self.date_updated = self.modified
    def before_save(self):
        # self.syncstatus = "false"
        # for saving
        if self.colorandshape:

            if not self.edit_color:

                colorAndShape = json.loads(self.colorandshape)[0]

                colors = {
                    "tomato": "Tomato",
                    "firebrick": "Fire Brick",
                    "blue": "Blue",
                    "gray": "Gray",
                    "green": "Green",
                    "darkorange": "Dark Orange",
                    "darkmagenta": "Dark Magenta"
                }

                self.color = colors[colorAndShape['color']]
                self.shape = colorAndShape['shape'].capitalize()

    def on_update(self):

        flags = self.__dict__['flags']

        if not flags.in_insert:

            # Frappe
            if self.edit_color:

                color = self.color.lower().replace(" ", "")
                shape = self.shape.lower()

                colorAndShape = [{ "color": color, "shape": shape }]

                self.colorandshape = json.dumps(colorAndShape).replace(" ", "")
                self.edit_color = 0

                if not self.from_couchdb:
                    document_on_update(self)

            # CouchDB
            else:
                colorAndShape = json.loads(self.colorandshape)[0]

                colors = {
                    "tomato": "Tomato",
                    "firebrick": "Fire Brick",
                    "blue": "Blue",
                    "gray": "Gray",
                    "green": "Green",
                    "darkorange": "Dark Orange",
                    "darkmagenta": "Dark Magenta"
                }

                self.color = colors[colorAndShape['color']]
                self.shape = colorAndShape['shape'].capitalize()

                if not self.from_couchdb:
                    document_on_update(self)

    def on_trash(self):
        document_on_trash(self)