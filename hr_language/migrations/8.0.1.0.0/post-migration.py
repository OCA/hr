# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    if not version:
        return

    cr.execute('''
        UPDATE hr_language a
            SET
                read_rating=(
                    CASE WHEN a.can_read IS TRUE THEN '3' ELSE '0' END),
                speak_rating=(
                    CASE WHEN a.can_speak IS TRUE THEN '3' ELSE '0' END),
                write_rating=(
                    CASE WHEN a.can_write IS TRUE THEN '3' ELSE '0' END)
        ''')

    cr.execute("""
        DELETE FROM ir_model_data
        WHERE   name = 'field_hr_language_can_read' AND
                module = 'hr_language' AND
                model = 'ir.model.fields'
        """)

    cr.execute("""
        DELETE FROM ir_model_data
        WHERE   name = 'field_hr_language_can_speak' AND
                module = 'hr_language' AND
                model = 'ir.model.fields'
        """)

    cr.execute("""
        DELETE FROM ir_model_data
        WHERE   name = 'field_hr_language_can_write' AND
                module = 'hr_language' AND
                model = 'ir.model.fields'
        """)

    cr.execute("""
        DELETE FROM ir_model_fields AS a
        USING    ir_model AS b
        WHERE   a.name = 'can_read' AND
                b.name = 'hr.language' AND
                a.model_id = b.id
        """)

    cr.execute("""
        DELETE FROM ir_model_fields AS a
        USING    ir_model AS b
        WHERE   a.name = 'can_speak' AND
                b.name = 'hr.language' AND
                a.model_id = b.id
        """)

    cr.execute("""
        DELETE FROM ir_model_fields AS a
        USING    ir_model AS b
        WHERE   a.name = 'can_write' AND
                b.name = 'hr.language' AND
                a.model_id = b.id
        """)

    cr.execute("""
        ALTER TABLE hr_language
            DROP COLUMN IF EXISTS can_read
            """)

    cr.execute("""
        ALTER TABLE hr_language
            DROP COLUMN IF EXISTS can_speak
            """)

    cr.execute("""
        ALTER TABLE hr_language
            DROP COLUMN IF EXISTS can_write
            """)
