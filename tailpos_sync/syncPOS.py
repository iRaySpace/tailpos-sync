# from frappe.utils import nowdate
# from couchdb import client
from events import document_on_trash, document_on_update, document_on_save
import frappe
import datetime
import json, time
import uuid
SERVER_URL = "https://admin:qwerty@db.tailpos.com"

@frappe.whitelist()
def syncData(data):
    sampleData = data
    owner = "Administrator"

    for check in sampleData['trashObject']:
        check_existing_deleted_item = frappe.db.sql("SELECT * FROM" + "`tab" + check['table_name'] + "` WHERE id=%s ",
                          (check['trashId']))
        if len(check_existing_deleted_item) > 0:

            frappe.db.sql("DELETE FROM" + "`tab" + check['table_name'] + "` WHERE id=%s ",
                          (check['trashId']))

    for i in range(0,len(sampleData['tailposData'])):
        receipt_total = 0
        print("nibalik diay sa loop")

        try:
            exist = frappe.db.sql("SELECT * FROM" + "`tab" + sampleData['tailposData'][i]['dbName'] + "` WHERE name=%s ", (sampleData['tailposData'][i]['syncObject']['_id']))
        except Exception:
            print(frappe.get_traceback())
        print("wala gyud kay")
        if sampleData['tailposData'][i]['dbName'] == "Receipts":
            existLines = frappe.db.sql(
                "SELECT * FROM `tabReceipts Item` WHERE parent=%s ",
                (sampleData['tailposData'][i]['syncObject']['_id']))

            if len(existLines) == 0:
                if len(sampleData['tailposData'][i]['syncObject']['lines']) > 0:
                     for x in range(0,len(sampleData['tailposData'][i]['syncObject']['lines'])):
                        print("NISULOD SA LINNNNNEEEESSSS")
                        receipt_total += int(sampleData['tailposData'][i]['syncObject']['lines'][x]['price']) * int(sampleData['tailposData'][i]['syncObject']['lines'][x]['qty'])
                        print(int(sampleData['tailposData'][i]['syncObject']['lines'][x]['price']))
                        print(int(sampleData['tailposData'][i]['syncObject']['lines'][x]['qty']))
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

            frappe_table = frappe.get_doc(sampleData['tailposData'][i]['dbName'], sampleData['tailposData'][i]['syncObject']['_id'])
        else:
            if sampleData['tailposData'][i]['dbName'] == "Item":
                try:
                    frappe_table = frappe.get_doc({
                        "doctype": sampleData['tailposData'][i]['dbName'],
                        "id": sampleData['tailposData'][i]['syncObject']['_id'],
                        "item_code": sampleData['tailposData'][i]['syncObject']['name'],
                        "item_group": "All Item Groups",
                        "item_name": sampleData['tailposData'][i]['syncObject']['name'],
                        "owner": owner
                    })

                except Exception:
                    print(frappe.get_traceback())

            else:
                try:
                    frappe_table = frappe.get_doc({
                        "doctype": sampleData['tailposData'][i]['dbName'],
                        "id": sampleData['tailposData'][i]['syncObject']['_id'],
                        "owner": owner
                    })

                except Exception:
                    print(frappe.get_traceback())

        date_from_pos = datetime.datetime.fromtimestamp(sampleData['tailposData'][i]['syncObject']['dateUpdated']/1000.0)

        if frappe_table.modified == None:

            update_data = True
            frappe_table.db_set("date_updated", None)
        else:
            if frappe_table.modified < date_from_pos:

                update_data = True
                frappe_table.db_set('date_updated', None)
            else:
                update_data = False
        if update_data:
            for key,value in sampleData['tailposData'][i]['syncObject'].iteritems():

                field_name = str(key).lower()

                if field_name == "taxes":
                    value = ""
                if field_name == "soldby":
                    field_name = "stock_uom"
                if field_name == "colorandshape":
                    field_name = "color_and_shape"
                if field_name == "colororimage":
                    field_name = "color_or_image"
                if field_name == "imagepath":
                    field_name = "image"
                if field_name == "price":
                    field_name = "standard_rate"
                if sampleData['tailposData'][i]['dbName'] != "Customer":
                    if field_name == "name":
                        field_name = "description"
                elif sampleData['tailposData'][i]['dbName'] == "Customer":
                    if field_name == "name":
                        field_name = "customer_name"
                if value == "No Category":
                    value = ""
                if value == "fixDiscount":
                    frappe_table.db_set("type", "Fix Discount")
                if value == "percentage":
                    frappe_table.db_set("type", "Percentage")


                elif field_name == "date":
                    # JavaScript milliseconds timestamp to Python seconds timestamp
                    print("DAAATE")
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

                except:
                    None
            try:
                if sampleData['tailposData'][i]['dbName'] == "Receipts":

                    try:
                        frappe_table.db_set("total_amount", receipt_total)
                    except Exception:
                        print(frappe.get_traceback())

                frappe_table.insert(ignore_permissions=True)
            except Exception:
                print("exception")
                print(frappe.get_traceback())

    erpnext_data = ""
    if sampleData['typeOfSync'] == "forceSync":
        erpnext_data = forceSyncFromErpnextToTailpos()
    elif sampleData['typeOfSync'] == "sync":
        erpnext_data = syncFromErpnextToTailpos()
    return {"data": {"data": erpnext_data}}

def forceSyncFromErpnextToTailpos():
    print("SUCCESS")

    tableNames = ['Item','Categories','Discounts','Attendants', "Customer"]
    data = []
    for i in tableNames:
        print(i)
        dataFromDb = frappe.db.sql("SELECT * FROM `tab" + i + "`", as_dict=True)
        print("jsdhlajsd")
        for x in dataFromDb:
            data.append({
                'tableNames': i,
                'syncObject': x
            })
            frappe.db.sql("UPDATE `tab" + i + "` SET `date_updated`=`modified` where id=%s", (x.id))
    return data

def syncFromErpnextToTailpos():
    print("SUCCESS")

    table_names = ['Item','Categories','Discounts','Attendants', 'Customer']
    data = []
    for i in table_names:
        print(i)
        dataFromDb = frappe.db.sql("SELECT * FROM `tab" + i + "` WHERE `modified` > `date_updated`",as_dict=True)

        print("SYYYYYNNNCCC")
        print(dataFromDb)
        if len(dataFromDb) > 0:
            for x in dataFromDb:
                data.append({
                    'tableNames': i,
                    'syncObject': x
                })
                frappe.db.sql("UPDATE `tab" + i + "` SET `date_updated`=`modified` where id=%s", (x.id))
    return data


@frappe.whitelist()
def save_item(doc,method):
    if doc.date_updated == None:
        print("sdadasdasd")
        doc.date_updated = doc.modified

@frappe.whitelist()
def autoname_item(doc,method):
    print("autonaaame")
    if not doc.id:
        doc.id = 'Item/' + str(uuid.uuid4())
    doc.name = doc.id
    print("niabot man")
@frappe.whitelist()
def after_insert(doc,method):

    if not doc.from_couchdb:
        colorAndShape = [{
            "color": doc.color.lower().replace(" ", ""),
            "shape": doc.shape.lower()
        }]

        skeleton_doc = {
            "_id": doc.id,
            "name": doc.description,
            "soldBy": doc.soldby,
            "price": doc.price or 0.00,
            "sku": doc.sku or "",
            "barcode": doc.barcode or "",
            "imagePath": "",
            "colorAndShape": json.dumps(colorAndShape).replace(" ", ""),
            "colorOrImage": "",
            "favorite": "",
            "category": doc.category_link or "",
            "taxes": ""
        }

        document_on_save(skeleton_doc, doc.__dict__['doctype'])
@frappe.whitelist()
def before_save(doc,method):
    doc.syncstatus = "false"
    if doc.from_couchdb and doc.colorandshape:

        setting = json.loads(doc.colorandshape)[0]

        colors = {
            "tomato": "Tomato",
            "firebrick": "Fire Brick",
            "blue": "Blue",
            "gray": "Gray",
            "green": "Green",
            "darkorange": "Dark Orange",
            "darkmagenta": "Dark Magenta"
        }

        if not doc.category == "No Category":
            doc.category_link = doc.category

        doc.color = colors[setting['color']]
        doc.shape = setting['shape'].capitalize()
@frappe.whitelist()
def on_update(doc,method):

    flags = doc.__dict__['flags']

    if not flags.in_insert:

        if doc.edit_colorandshape:

            color = doc.color.lower().replace(" ", "")
            shape = doc.shape.lower()

            colorAndShape = [{"color": color, "shape": shape}]

            doc.colorandshape = json.dumps(colorAndShape).replace(" ", "")
            doc.category = doc.category_link
            doc.edit_color = 0

            if not doc.from_couchdb:
                document_on_update(doc)

        else:

            colorAndShape = json.loads(doc.colorandshape)[0]

            colors = {
                "tomato": "Tomato",
                "firebrick": "Fire Brick",
                "blue": "Blue",
                "gray": "Gray",
                "green": "Green",
                "darkorange": "Dark Orange",
                "darkmagenta": "Dark Magenta"
            }

            doc.color = colors[colorAndShape['color']]
            doc.shape = colorAndShape['shape'].capitalize()

            if not doc.from_couchdb:
                document_on_update(doc)
@frappe.whitelist()
def on_trash(doc,method):
    document_on_trash(doc)