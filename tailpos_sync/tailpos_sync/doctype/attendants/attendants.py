# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from tailpos_sync.events import document_on_update, document_on_trash, document_on_save

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
		# self.syncstatus = "false"
		print("PPPIIIINNNSSS")
		print(self.modified)
		print(self.date_updated == None)
		if self.pin_code != None:
			length = len(self.pin_code)

			if (int(length) != 4):
				frappe.throw(_("PIN Code should contain 4 numbers only."))

			try:
				pin_code = int(self.pin_code)
			except:
				frappe.throw(_("PIN Code should be a number."))
		if self.date_updated == None:
			print("sdadasdasd")
			self.date_updated = self.modified

	def on_trash(self):
		document_on_trash(self)