Allow a calendar to alternate between multiple weeks.

An implementation of this functionality exists in Odoo's ``resource`` module
since version 13. In Odoo's implementation, you can only alternate between two
weeks. Furthermore, the implementation is more than a little wonky.

The advantage of this module over the implementation in ``resource`` is that you
can alternate between more than two weeks. The implementation is (hopefully)
better.

The downside of adopting this module is that all modules which interact with the
week-alternating functionality of ``resource`` must be adapted to be compatible
with this module. At the time of writing (2024-07-29), the only Odoo module
which does this is ``hr_holidays``.
