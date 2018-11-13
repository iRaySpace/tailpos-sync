frappe.listview_settings['Receipts'] = {
    refresh: function (me) {
        frappe.call({
            method: "tailpos_erpnext.rests.sync_doctype",
            args: {
                "doctype": "receipts"
            }
        });
    }
}