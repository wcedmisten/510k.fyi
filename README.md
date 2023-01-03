# Install tesseract and graphviz

```
sudo apt-get install tesseract-ocr graphviz
```

# Install requirements

```
pip3 install -r requirements.txt
```

# File sources

Device dataset downloaded from: https://open.fda.gov/apis/device/510k/download/

```
wget https://download.open.fda.gov/device/510k/device-510k-0001-of-0001.json.zip
unzip device-510k-0001-of-0001.json.zip
```

Recall dataset downloaded from: https://open.fda.gov/apis/device/recall/download/

```
wget https://download.open.fda.gov/device/recall/device-recall-0001-of-0001.json.zip
unzip device-recall-0001-of-0001.json.zip
```

Import the JSON data to a SQLite Database

```
python3 db_import.py
```

Scrape the FDA website and download PDFs for 510(k) summary statements.

```
python3 scrape.py
```

Visualize a graph of the 510(k) dependencies

```
python3 visualize.py
```

This should produce a graph like this:

![Graph](screenshots/ancestry.png)
