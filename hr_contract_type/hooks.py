def post_init_hook(cr, registry):
    """Check if the field comes from 12 and rename the column"""
    cr.execute(
        "SELECT count(attname) FROM pg_attribute "
        "WHERE attrelid = "
        "( SELECT oid FROM pg_class WHERE relname = %s ) "
        "AND attname = %s",
        ("hr_contract", "type_id"),
    )
    if cr.fetchone()[0] == 1:
        cr.execute(
            """
        UPDATE hr_contract
        SET contract_type_id = type_id
        WHERE type_id IS NOT NULL
        """,
        )
