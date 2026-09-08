# swatt-api

App to manage my store orders.

## Contributing

Please run the following to start contributing, this grabs dependencies and make githook runs:

```bash
uv sync
uv run pre-commit install
```

## Business requirements

The following is the business requirements:
- Staff explicitly says that they work with lowercase, no extra whitespaces, "names" only. So that means item name, lookup table names, person name, address. All are deliberate to be in lowercase and unique. Because how the staff works without application is that they use pen and paper and Android phone to track contacts. And they manually come up with unique names for the contacts and the rest of things they write down that refer to something. There are no meaningful distinction when the casing differ, staff primarily works with just letters disregarding the casing at all and duplicates and extra white spaces are never meaningful at all too.
- Staff says that a person always have one phone but they have many addresses by design.
- Staff says that an order can be made to the same person or different person.
- Staff never deletes as well, if they do not use it? They just won't use it no more. No one is diligent enough to prune unused items. When they work with pen and paper when things are not being used no more they just won't write it down.
