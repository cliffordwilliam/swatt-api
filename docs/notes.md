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

## Partial index condition (postgresql_where)

The documentation says that I have to use postgresql_where but it does not explicitly say what value it expects. So after tyring and what worked is that I have to use the text construct and passes what comes after the WHERE in sql instructions.

postgresql_where=text("deleted_at IS NULL")

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

I need to add # noqa: UP037 when I have the following Mapped[list["PersonPhone"]]. There is another way where I have to import something but I figured just a few character comments is fine rather than introducing more things. This way its just a few comment character while keeping the codebase aligned with how the documentation wants it. This avoids odd suprises in the future.


## How testing works using pytest fixture with alembic

So on start of the whole test, it needs to create test engine and call alembic migration. On whole test ends it would dispose engine. Per test gotta setup fresh session, on each test ends gotta cleanup the session, undo any changes in database state, connection and transaction. This is so that each test is always provided a clean slate session, just seed, then go for any tests it needs right there.
