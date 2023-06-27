## New feature:

- **Milking option:** a possibility to run dry the entire wallet. The principle is the following:
    1. Pick the max size of the single transaction
    2. Run these transactions until "Insufficient balance" notice
    3. Decrease the size of the single transaction by 1/2
    4. Repeat until no reasonable size is possible

Implementation, while not difficult, requires rethinking of the UI. For instance what should the default be? Is the
config file necessary? 