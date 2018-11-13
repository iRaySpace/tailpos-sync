from frappe.utils import nowdate
from couchdb import client
import frappe
import datetime
import json, time
SERVER_URL = "https://admin:qwerty@db.tailpos.com"

@frappe.whitelist(allow_guest=True)
def syncData(data):
    sampleData = json.loads(data)
    print("TABLE NAAAAAAAAAME")
    print(sampleData)
    owner = "Administrator"
    # print("======================================================")
    # print(datetime.datetime.fromtimestamp(sampleData['sampleData'][0]['dateUpdated']/1000.0))
    # print("======================================================")
    # print("LENGTH")
    # print(len(sampleData))
    for i in range(0,len(sampleData['tailposData'])):
        # print("NISULOD SA FOR LOOP")
        exist = frappe.db.sql("SELECT * FROM" + "`tab" + sampleData['tailposData'][i]['dbName'] + "` WHERE name=%s ", (sampleData['tailposData'][i]['syncObject']['_id']))
        # print("LEEENGTH")
        # print(exist)
        if sampleData['tailposData'][i]['dbName'] == "Receipts":
            existLines = frappe.db.sql(
                "SELECT * FROM `tabReceipts Item` WHERE parent=%s ",
                (sampleData['tailposData'][i]['syncObject']['_id']))

            # print("RECEIPTS LIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIINES")
            if len(existLines) == 0:
                if len(sampleData['tailposData'][i]['syncObject']['lines']) > 0:
                    for x in range(0,len(sampleData['tailposData'][i]['syncObject']['lines'])):
                        print("NISULOD SA LINNNNNEEEESSSS")
                        try:
                            doc = {'doctype': 'Receipts Item',
                                   'parent': str(sampleData['tailposData'][i]['syncObject']['_id']),
                                   'parenttype': "Receipts",
                                   'parentfield': "receipt_lines",
                                   'item_name': sampleData['tailposData'][i]['syncObject']['lines'][x]['item_name'],
                                   'sold_by': sampleData['tailposData'][i]['syncObject']['lines'][x]['sold_by'],
                                   'price': sampleData['tailposData'][i]['syncObject']['lines'][x]['price'],
                                   'qty': sampleData['tailposData'][i]['syncObject']['lines'][x]['qty']
                                   }
                            doc1 = frappe.get_doc(doc)
                            doc1.insert(ignore_permissions=True)

                        except Exception:
                            print(frappe.get_traceback())
        if len(exist) > 0:
            print("EXIIIST")
            frappe_table = frappe.get_doc(sampleData['tailposData'][i]['dbName'], sampleData['tailposData'][i]['syncObject']['_id'])
        else:
            try:
                frappe_table = frappe.get_doc({
                    "doctype": sampleData['tailposData'][i]['dbName'],
                    "id": sampleData['tailposData'][i]['syncObject']['_id'],
                })
                frappe_table.insert(ignore_permissions=True)
            except Exception:
                print(frappe.get_traceback())
        # dateUpdated = datetime.datetime.fromtimestamp(sampleData['sampleData'][i]['dateUpdated']/1000.0)
        # print("ITERITEEEEEMS"
        for key,value in sampleData['tailposData'][i]['syncObject'].iteritems():
            # print(key)
            # print("DATAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            field_name = str(key).lower()
            if field_name == "name":
                field_name = "description"
            elif field_name == "date":
                # JavaScript milliseconds timestamp to Python seconds timestamp
                if value:
                    if sampleData['tailposData'][i]['dbName'] != "Receipts":
                        value = datetime.datetime.fromtimestamp(value / 1000.0).date()
                    else:
                        value = datetime.datetime.fromtimestamp(value / 1000.0)

            elif field_name == "shift_beginning" or field_name == "shift_end":
                if value:
                    value = datetime.datetime.fromtimestamp(value / 1000.0)
            elif field_name == "lines":
                value = json.dumps(value)
            try:
                frappe_table.db_set(field_name, value)
                # print("OKAAAY")
            except:
                None
        try:
            frappe_table.save(ignore_permissions=True)
        except Exception:
            print(frappe.get_traceback())
        print("MANA UG SAVE")

        frappe.db.sql("UPDATE " + "`tab" + sampleData['tailposData'][i]['dbName'] + "` SET modified_by=%s, owner=%s WHERE name = %s",
                      (owner, owner, frappe_table.name))
        print("MANA")

