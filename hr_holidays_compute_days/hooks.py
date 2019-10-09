# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(cr):
    """Default all existing leaves for not being full day precreating both
    boolean columns.
    """
    cr.execute("ALTER TABLE hr_holidays ADD from_full_day BOOLEAN")
    cr.execute("ALTER TABLE hr_holidays ADD to_full_day BOOLEAN")
