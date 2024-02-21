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
* Allow user to switch to table view instead of graph view to see all data at once
* Show recall dates
* Improve recall formatting
* Add query params to URL for currently focused device (e.g. `?device=K102465`)
