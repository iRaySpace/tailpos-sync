# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tailpos_sync.events import document_on_trash, document_on_update, document_on_save
import uuid

class Taxes(Document):
	def autoname(self):
		if not self.id:
			self.id = 'Tax/' + str(uuid.uuid4())
		self.name = self.id

	def after_insert(self):
		if not self.from_couchdb:
			skeleton_doc = {
				"_id": self.id,
				"name": self.description,
				"rate": self.rate,
				"type": self.type,
				"option": self.option,
				"activate": self.activate
			}
			document_on_save(skeleton_doc, self.__dict__['doctype'])

	def on_trash(self):
		document_on_trash(self)