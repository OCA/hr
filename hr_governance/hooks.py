# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def set_root_circle_name(env):
    """Changing the name of the root circle by the company name"""
    root_circle = env.ref("hr_governance.root")
    root_circle.write({"name": env.company.name})


def post_init_hook(env):
    set_root_circle_name(env)
