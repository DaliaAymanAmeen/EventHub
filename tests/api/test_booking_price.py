from decimal import Decimal

import pytest

from data.factories import booking_payload

pytestmark = pytest.mark.api

# A2 | AC2 | totalPrice = event price × quantity (min, typical, max)
@pytest.mark.parametrize("quantity", [1, 3, 10])
def test_total_price_is_ticket_price_times_quantity(test_event, create_booking, quantity):
    response = create_booking(booking_payload(test_event["id"], quantity=quantity))
    assert response.status == 201, response.text()

    total_price = Decimal(str(response.json()["data"]["totalPrice"]))

    expected = Decimal(str(test_event["price"])) * quantity
    assert total_price == expected



# A13 | AC2 | totalPrice returned as a number, as documented (known bug)
@pytest.mark.xfail(
    reason="BUG: docs say totalPrice is a number, API returns a string (e.g. '299.97')",
    strict=True,
)
def test_total_price_is_returned_as_number(test_event, create_booking):
    response = create_booking(booking_payload(test_event["id"]))
    assert response.status == 201, response.text()

    total_price = response.json()["data"]["totalPrice"]


    assert isinstance(total_price, (int, float)), f"Got {type(total_price).__name__}: {total_price!r}"