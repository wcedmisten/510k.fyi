# 510k.fyi webapp

Meant to provide better search features for the FDA's 510k dataset and provide structured data on predicate devices.

To run:

```
cp ../devices.db ./backend
```

For development:

```
docker compose -f docker-compose-dev.yml
```

For prod:

```
docker compose -f docker-compose-dev.yml
```

## Todo:

* Add landing page
* Move search to postgres
* Use fuzzy string search in postgres
