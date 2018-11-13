# -*- coding: utf-8 -*-
# Copyright (c) 2018, Bai Web and Mobile Lab and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
import uuid

class Receipts(Document):
	def autoname(self):
		if not self.id:
			self.id = 'Receipt/' + str(uuid.uuid4())
		self.name = self.id

	def validate(self):
		self.series = "Receipt %s - %s" % (self.receiptnumber, self.date)

