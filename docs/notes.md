# Notes

This document store important notes about how to work on this project.

## Use PostgreSQL TIMESTAMP in mapped classes

The reason is that it always store as UTC. If the incoming value has timezone information then it will use that to compute the UTC. If the incoming does not have it then it will use the session's timezone to compute the UTC. So the DDL must show TIMESTAMP WITH TIME ZONE.

The session here is referring to connection. So if incoming value has no timezone information, it will use the connection's timezone information instead.

The CURRENT_TIMESTAMP here uses UTC already so there are no conversion that is going to happen when we do created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL.

## Constraint mapped classes naming convention

In here, I need to explicitly name the check constraint. This is also good because if a column has more than one constraint then explicit naming is needed to prevent naming conflict.

Use this format, <column>_<description>, for example: item_price_positive

## Commit message format

Here is an example:

```text
fix: prevent race condition in token refresh

Token refresh could fire twice if two requests hit a 401
simultaneously. Added a mutex so only one refresh happens
at a time; concurrent requests await the same promise.
```

Types to use:
- feat: new feature
- fix: bug fix
- docs: documentation only
- style: formatting, no code change
- refactor: code change that's neither a fix nor a feature
- test: adding/fixing tests
- chore: tooling, dependencies, build config


## Migration file naming convention

file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s

Always name it explicitly too with -m, like so:

uv run --env-file .env alembic revision --autogenerate -m "add_email_verified_to_users"

Here is a format to follow:

```text
<verb>_<subject>[_<detail>]
```

Examples:
- create_initial_tables
- add_users_table
- add_index_users_email
- drop_legacy_orders_status_column
- alter_products_price_to_numeric
- rename_customer_to_client
- create_fk_orders_user_id

## Never delete, snapshot next to every FK

Staff never delete on paper, they just stop writing old things down. So the app has no delete feature at all, only create, read and update. This keeps things simple:
- Every FK is required, `Mapped[int]`, since what it points at never disappears.
- No `ondelete` needed. The default FK behavior already blocks deleting a row that is referenced, which is a free safety net.
- No `deleted_at` column, no partial unique index, no filtering deleted rows. Plain unique constraints are enough.
- Every FK on orders has a required snapshot column next to it, e.g. `buyer_id` and `buyer_name`, `delivery_method_id` and `delivery_method_name`. Editing the live record, like fixing a typo, never changes past orders.

Search has two modes: search the snapshot for what was written on the order, or follow the FK for the current value.

Old unused entries will clutter pick lists over time. For now show the most recently used on top. If staff complain, add a `hidden` flag that only affects pick lists.

## Updated at trigger

I cannot create a trigger in mapped class and somehow have alembic make one for me in the migration file when using the alembic autogenerate feature. So instead I have first created a migration that adds a function called `create set_updated_at trigger function`. What it does is that it adds a new function called set_updated_at. Then subsequent tables that needs auto filling updated_at value just needs to create a trigger that uses it. So that means each time I auto generate a table, I need to edit it by hand so that it creates a trigger that uses that function. Note the naming convention is like this `<table_name>_set_updated_at`, e.g. `blogs_set_updated_at`. Here is an example on what to add per migration file:

```py
# After upgrade auto generated lines
    op.execute("""
        CREATE TRIGGER items_set_updated_at
        BEFORE UPDATE ON items
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)

# Before downgrade auto generated lines
    op.execute("""
        DROP TRIGGER IF EXISTS items_set_updated_at ON items;
    """)
```

## Using uv to read value from .env instead of using dotenv package

This uses uv built in feature to read value from env memory block. It uses the --env-file .env flag in uv run command.

## Alembic config

Alembic already uses the ini getter and setter in many places, so the smaller change would be to just set the .ini value using the env block value rather than replacing all references of the .ini file with the direct env block value.

## Ruff issue with string types in mapped classes

I need to add # noqa: UP037 when I have the following Mapped[list["PersonAddress"]]. There is another way where I have to import something but I figured just a few character comments is fine rather than introducing more things. This way its just a few comment character while keeping the codebase aligned with how the documentation wants it. This avoids odd suprises in the future.


## How testing works using pytest fixture with alembic

So on start of the whole test, it needs to create test engine and call alembic migration. On whole test ends it would dispose engine. Per test gotta setup fresh session, on each test ends gotta cleanup the session, undo any changes in database state, connection and transaction. This is so that each test is always provided a clean slate session, just seed, then go for any tests it needs right there. To make each test be able to commit without causing real changes in the database we use the "nested transaction rollback", where commit per test works against the inner SAVEPOINT and not the outer at all, the outer per test would rollback safely. This then in turn needs pooling to be turned off otherwise there may be issues with the nested transaction implementation. But the main point is that if we turn off pooling, we guarantee connection is never reused, we do not want previous connection to be reused since it is stateful like it carries its SAVEPOINT attributes with it.

How SAVEPOINT works in a nutshell. Think of transaction as a private workbench, you do actions in there and what happens in there is only visible in that workbench. Once you are happy with the actions, you either commit to tear down the workbench and submit the work you have done to the public, or you rollback to tear down the workbench wihtout submitting anything. SAVEPOINT is a feature used during working in a workbench, where you create SAVEPOINT markers, do a bunch of actions, then either you are happy with it and keep your work and remove the SAVEPOINT or you rollback to go back to your SAVEPOINT and discard all your work. So initially the tests here when they do commit, it causes the transaction to be tore down and the work to be submitted. But now when the tests commit, it causes the old SAVEPOINT to be removed and a new one is created.


## Errors from mapped classes like from its constraints

The documentations only mentions error classes caused by dbapi. It does not mention like what error would a table constraint throw, so I need to do trial and error by running to cause a deliberate error to show in my stdout to know what it thorws.


## Testing error raises with session

During testing, if the raise did happen, the session state itself needs to be rolledback, otherwise, the fixture trying to cleanup the session won't work. So I have to rollback per raises I do, that way the session state is in good shape to be used normally.

Always pass `match=` with the constraint or column name, e.g. `raises(IntegrityError, match="ck_items_name_normalized")`. Every constraint violation is an IntegrityError, so without `match=` the test can pass for the wrong reason, like a missing required column instead of the check I meant to test. Also make sure the rest of the row is valid so only the thing under test is wrong.

## Making FK required with Mapped

We can use the mapped_column.nullable attribute but that does not add typing. So instead we rely primarily on Mapped to govern if its required or not. Note that if the type is BigInt but we Mapped[int] its okay because the FK would infer based on what it is pointing at so it will correctly store it in db as BigInt and you get to work with int.
