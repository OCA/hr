To use this module, you need to:

1.  Install the module in your Odoo database.

2.  Ensure employees have their "Work Contact" field properly linked:

    -   Go to the "Employees" app.
    -   Select an employee.
    -   In the "Work Contact" field, verify the contact is set.

3.  Verify the restriction works:

    -   As a user with accounting rights (Accounting User or Accounting Manager),
        open a contact linked to an employee. The bank accounts section should be visible.

    -   As a user without accounting rights (like Billing or Internal User),
        open a contact linked to an employee. The bank accounts section should be hidden.

4.  For regular contacts (not related to employees), bank accounts are always visible
    to all users.