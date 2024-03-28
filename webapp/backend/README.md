```
apt install uvicorn
pip3 install -r requirements.txt
```

```
uvicorn main:app --reload
```

## Importing the data once docker is running

```
docker exec -it webapp-backend-1 bash
cd app/
python3 db_import.py
```
