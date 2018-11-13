frappe.listview_settings['Shifts'] = {
  refresh: function (me) {
    frappe.call({
      method: "tailpos_erpnext.rests.sync_doctype",
      args: {
        "doctype": "shifts"
      }
    });
  }
}