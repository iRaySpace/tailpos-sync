# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe import _
from tailpos_erpnext.events import document_on_save, document_on_trash
import frappe
import uuid

class Attendants(Document):
	def autoname(self):
		if not self.id:
			self.id = 'Attendant/' + str(uuid.uuid4())
		self.name = self.id

	def after_insert(self):

		if not self.from_couchdb:

			skeleton_doc = {
				"_id": self.id,
				"user_name": self.user_name,
				"pin_code": self.pin_code,
				"role": self.role
			}

			document_on_save(skeleton_doc, self.__dict__['doctype'])

	def validate(self):
		length = len(self.pin_code)

		if (int(length) != 4):
			frappe.throw(_("PIN Code should contain 4 numbers only."))

		try:
			pin_code = int(self.pin_code)
		except:
			frappe.throw(_("PIN Code should be a number."))

	def on_trash(self):
		document_on_trash(self)