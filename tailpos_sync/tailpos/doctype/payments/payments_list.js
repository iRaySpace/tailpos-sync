frappe.listview_settings['Payments'] = {
  refresh: function (me) {
    frappe.call({
      method: "tailpos_erpnext.rests.sync_doctype",
      args: {
        "doctype": "payments"
      }
    });
  }
}