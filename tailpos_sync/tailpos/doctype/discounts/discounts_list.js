frappe.listview_settings['Discounts'] = {
    refresh: function (me) {
        frappe.call({
            method: "tailpos_erpnext.rests.sync_doctype",
            args: {
                "doctype": "discounts"
            }
        });
    },
};