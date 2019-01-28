* Previously filled values are erased when changing employee, leave type,
  or date range selection. This is caused by limitation of Odoo that it's
  impossible to read ``one2many`` fields in ``onchange`` handlers, so no
  way to check which entry should be persisted.
