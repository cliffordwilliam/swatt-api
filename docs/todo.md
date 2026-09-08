# TODO

This document holds the list of things I plan to do in the future so that I do not forget.

- [ ] Review the dependencies version in my pyproject.toml file
- [ ] Review the dependencies that I need to change later in production such as the `psycopg[binary]`
- [ ] Staff writes sloppy so need to trim extra spaces on either end and betweens. But allow them to type in mixed capitalization. Just make sure to allow case insensitive filter. Add this to notes.md on decision on how to tackle this issue.
- [ ] Do not forget to add the updated_at trigger and function per table later, follow the guide in the neighboring file notes.md.
- [ ] Raise and exit early when reading env values and its not right. There is no recovering from that.
- [ ] Deal with nullable FK, either prevent deletion when they are referred to, or prevent deletion on user level.
- [ ] Centralize the regex into one file and use it everywhere? That way its not duplicated all over the place.
- [ ] Lookup have no snapshot? Unlikely to be deleted or edited so maybe fine for now. Staff always append only anyways. But if they did a typo and create one and wish to edit then that is when we need to snapshot I think to respect history.
- [ ] Create pytest for the SQLAlchemy stuff first, this need throwaway database too, test stuff like the input checks, the price checks and so on.
- [ ] Then create the FastAPI routes.
