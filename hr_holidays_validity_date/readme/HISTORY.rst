At first this module added two new fields to the Leave Type model, the
start and the end of a range that meant the time interval where that type
could be requested.

In 11.0 it was added that it could be chosen whether this was a constraint or
simply a message.

In 12.0 Odoo added the range feature in their Leaves module (validity_start and
validity_stop) so nowadays this just
adds the feature that lets you chose if you want a warning or a constraint.
