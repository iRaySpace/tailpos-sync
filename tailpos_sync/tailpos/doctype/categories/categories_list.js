frappe.listview_settings['Categories'] = {
    refresh: function (me) {
        frappe.call({
            method: "tailpos_erpnext.rests.sync_doctype",
            args: {
                "doctype": "categories"
            }
        });
    },
};