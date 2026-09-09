from sqlalchemy import text


def test_add_record(test_session):
    sql_instruction = text(
        "INSERT INTO delivery_methods (name, created_at, updated_at) VALUES ('test', now(), now())"
    )
    test_session.execute(sql_instruction)
    test_session.commit()
    sql_instruction = text("SELECT count(*) FROM delivery_methods")
    result = test_session.execute(sql_instruction)
    number_of_existing_delivery_methods = result.scalar()
    assert number_of_existing_delivery_methods == 1


def test_sees_clean(test_session):
    sql_instruction = text("SELECT count(*) FROM delivery_methods")
    result = test_session.execute(sql_instruction)
    number_of_existing_delivery_methods = result.scalar()
    assert number_of_existing_delivery_methods == 0
