from pytest import raises
from sqlalchemy.exc import IntegrityError

from swatt_api.main import Item


def test_reject_item_with_negative_price(test_session):
    item_with_negative_price = Item(name="item with negative price", price=-1)
    test_session.add(item_with_negative_price)
    with raises(IntegrityError):
        test_session.commit()
