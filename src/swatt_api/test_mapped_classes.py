from pytest import raises
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from swatt_api.main import Item


def test_reject_item_with_negative_price(test_session):
    item_with_negative_price = Item(name="item with negative price", price=-1)
    test_session.add(item_with_negative_price)
    with raises(IntegrityError):
        test_session.commit()
    test_session.rollback()


def test_accept_item_with_zero_price(test_session):
    item_with_zero_price = Item(name="item with zero price", price=0)
    test_session.add(item_with_zero_price)
    test_session.commit()
    sql_instruction = select(Item).filter_by(id=item_with_zero_price.id)
    result = test_session.execute(sql_instruction)
    created_item = result.scalar_one()
    assert created_item.price == 0
