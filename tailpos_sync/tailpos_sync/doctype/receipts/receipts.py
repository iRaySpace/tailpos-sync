# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import uuid


class Receipts(Document):
	def validate(self):
		if self.date_updated == None:
			print("sdadasdasd")
			self.date_updated = self.modified

		if self.receipt_lines:
			print("RECEEEEEEEEEIPT LIIIIINEEES VALIDATE")
			print(self.receipt_lines)
	def set_default_values(self):
		"""Set the status as title-d form"""
		if self.flags.in_insert:
			self.status = self.status.title()
			self.series = 'Receipt/{0}'.format(self.receiptnumber)

	def autoname(self):
		if not self.id:
			self.id = 'Receipt/' + str(uuid.uuid4())
		self.name = self.id

	def before_save(self):
		"""Setup the Receipts document"""
		self.set_default_values()