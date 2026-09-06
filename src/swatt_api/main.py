from datetime import datetime
from typing import Annotated

from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    CheckConstraint,
    Computed,
    ForeignKey,
    MetaData,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import psycopg
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import CreateTable

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)


# Reusable.
timestamp = Annotated[
    datetime,
    mapped_column(TIMESTAMP(timezone=True), server_default=func.current_timestamp()),
]


class Item(Base):
    # This table represents store items.
    __tablename__ = "items"

    # There is not many store items so we use autoincrement int.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Item names are unique.
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # Store uses only IDR so it uses BigInteger, int maxes out about 2.1 billion.
    price: Mapped[int] = mapped_column(BigInteger)

    # Store in UTC, let clients render wall clock.
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="item")  # noqa: UP037

    __table_args__ = (
        # My store items cannot have negative price.
        CheckConstraint("price>=0", name="price_positive"),
    )


class DeliveryMethod(Base):
    # Lookup table. Records may be added over time but are never removed by staff.
    __tablename__ = "delivery_methods"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]


class PaymentMethod(Base):
    # Lookup table. Records may be added over time but are never removed by staff.
    __tablename__ = "payment_methods"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]


class OrderStatus(Base):
    # Lookup table. Records may be added over time but are never removed by staff.
    __tablename__ = "order_statuses"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]


class Person(Base):
    # Represents people who buy and receive items.
    __tablename__ = "persons"

    # There are many people in my store.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Filled using Android contact picker.
    name: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    phones: Mapped[list["PersonPhone"]] = relationship(back_populates="person")  # noqa: UP037
    addresses: Mapped[list["PersonAddress"]] = relationship(back_populates="person")  # noqa: UP037


class PersonPhone(Base):
    # This represent a person phone.
    __tablename__ = "person_phones"

    # Person does not have many phones.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Filled using Android contact picker.
    # Unique under a person namespace only using UniqueConstraint.
    phone_number: Mapped[str] = mapped_column(String(25))

    # Belong to one person.
    person_id = mapped_column(ForeignKey("persons.id"))

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    person: Mapped["Person"] = relationship(back_populates="phones")  # noqa: UP037

    __table_args__ = (
        # Ensure no duplicate link from person A to phone A more than once.
        UniqueConstraint("person_id", "phone_number"),
    )


class PersonAddress(Base):
    # This represent a person address.
    __tablename__ = "person_addresses"

    # Person does not have many addresses.
    id: Mapped[int] = mapped_column(primary_key=True)

    # Filled using Android contact picker.
    # Unique under a person namespace only using UniqueConstraint.
    address: Mapped[str] = mapped_column(Text)

    # This one is filled using map API, places pin coordinate.
    latitude: Mapped[float] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float] = mapped_column(Numeric(9, 6))

    # Belong to one person.
    person_id = mapped_column(ForeignKey("persons.id"))

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    person: Mapped["Person"] = relationship(back_populates="addresses")  # noqa: UP037

    __table_args__ = (
        # Ensure no duplicate link from person A to address A more than once.
        UniqueConstraint("person_id", "address"),
        # Input entry protection from accidental whitespaces.
        CheckConstraint(
            "address != '' AND address = TRIM(address)",
            name="address_no_stray_whitespace",
        ),
    )


class Order(Base):
    # This table represent my store orders.
    __tablename__ = "orders"

    # My store have many orders so we use BigInteger.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Staff likes to add nickname to the order, this is arbitrary.
    order_code: Mapped[str] = mapped_column(Text)

    # When order is made.
    order_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    # When order is to be delivered.
    delivery_date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))

    # Buyer pointer and on creation snapshot value.
    buyer_id = mapped_column(ForeignKey("persons.id"))
    buyer_name: Mapped[str] = mapped_column(String(255))
    buyer_phone: Mapped[str] = mapped_column(String(25))
    buyer_address: Mapped[str] = mapped_column(Text)

    # Recipient pointer and on creation snapshot value.
    recipient_id = mapped_column(ForeignKey("persons.id"))
    recipient_name: Mapped[str] = mapped_column(String(255))
    recipient_phone: Mapped[str] = mapped_column(String(25))
    recipient_address: Mapped[str] = mapped_column(Text)

    # Lookup table pointers.
    delivery_method_id = mapped_column(ForeignKey("delivery_methods.id"))
    payment_method_id = mapped_column(ForeignKey("payment_methods.id"))
    order_status_id = mapped_column(ForeignKey("order_statuses.id"))

    # Order money and precomputed values.
    shipping_cost: Mapped[int] = mapped_column(BigInteger)

    # Optional note filled by hand.
    note: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")  # noqa: UP037

    __table_args__ = (
        # Must order first, then deliver.
        CheckConstraint(
            "delivery_date >= order_date", name="delivery_not_before_order"
        ),
        # Shipping cost cannot be negative.
        CheckConstraint("shipping_cost >= 0", name="positive_shipping_cost"),
    )


class OrderItem(Base):
    # This table represent order item relations.
    __tablename__ = "order_items"

    # Relations.
    order_id = mapped_column(ForeignKey("orders.id"), primary_key=True)
    item_id = mapped_column(ForeignKey("items.id"), primary_key=True)

    # Item attribute snapshot at order time to respect history.
    item_name: Mapped[str] = mapped_column(String(100))
    item_price: Mapped[int] = mapped_column(BigInteger)

    # Quantity. No one would order too much anyways so int is fine here.
    quantity: Mapped[int]

    # Money.
    line_total: Mapped[int] = mapped_column(
        BigInteger, Computed("quantity * item_price")
    )

    created_at: Mapped[timestamp]
    updated_at: Mapped[timestamp]

    # Relations.
    order: Mapped["Order"] = relationship(back_populates="order_items")  # noqa: UP037
    item: Mapped["Item"] = relationship(back_populates="order_items")  # noqa: UP037

    __table_args__ = (
        # Price cannot be negative.
        CheckConstraint("item_price >= 0", name="positive_item_price"),
        # Quantity minimum is one.
        CheckConstraint("quantity > 0", name="minimum_one_quantity"),
    )


for table in Base.metadata.tables.values():
    print(CreateTable(table).compile(dialect=psycopg.dialect()).string)
    print(table.indexes)
