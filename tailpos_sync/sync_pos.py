from sync_methods import *
import frappe
import datetime


@frappe.whitelist()
def pull_data(data):
    query = "SELECT name FROM `tab{0}`".format(data['doctype'])

    if data['doctype'] == "Item":
        query = "SELECT name, description, standard_rate FROM `tabItem` WHERE disabled=0"

    # Getting the resources
    res = frappe.db.sql(query, as_dict=True)

    return {"data": res}


@frappe.whitelist()
def sync_data(data):
    #Check if there is Each and Weight in UOM
    uom_check()
    #Check if there are latest deleted records
    deleted_records = deleted_documents()

    #Delete records
    delete_records(data['trashObject'])

    for i in range(0,len(data['tailposData'])):
        receipt_total = 0

        # Check if record is existing in deleted documents
        if deleted_records_check(data['tailposData'][i]['syncObject']['_id'], deleted_records):
            try:
                exist = frappe.db.sql("SELECT * FROM" + "`tab" + data['tailposData'][i]['dbName'] + "` WHERE name=%s ", (data['tailposData'][i]['syncObject']['_id']))
            except Exception:
                print(frappe.get_traceback())
            if data['tailposData'][i]['dbName'] == "Receipts":
                #Add receipt lines
                receipt_total = add_receipt_lines(data['tailposData'],i)

            if len(exist) > 0:

                frappe_table = frappe.get_doc(data['tailposData'][i]['dbName'], data['tailposData'][i]['syncObject']['_id'])
            else:
                frappe_table = create_doc(data['tailposData'],i)
            #Check modified time


            update_data = check_modified(data['tailposData'][i]['syncObject']['dateUpdated'],frappe_table)

            if update_data:
                #Insert data

                insert_data(i,data['tailposData'],frappe_table,receipt_total)

    erpnext_data = ""
    if data['typeOfSync'] == "forceSync":
        #Fetch all data in ERPNext for selected tables

        erpnext_data = force_sync_from_erpnext_to_tailpos()

    elif data['typeOfSync'] == "sync":
        #Fetch Updated or Added data in ERPNext for selected tables
        erpnext_data = sync_from_erpnext_to_tailpos()
    return {"data": {"data": erpnext_data, "deleted_documents": deleted_records}}

def check_modified(data,frappe_table):
    date_from_pos = datetime.datetime.fromtimestamp(data / 1000.0)

    if frappe_table.modified == None:

        update_data = True
        frappe_table.db_set("date_updated", None)
    else:
        if frappe_table.modified < date_from_pos:

            update_data = True
            frappe_table.db_set('date_updated', None)
        else:
            update_data = False
    return update_data