# This repo is meant to help parse the FDA's 510k Summaries to derive predicate device information

## Installing

### Install tesseract and graphviz

```
sudo apt-get install tesseract-ocr graphviz
```

### Install requirements

```
pip3 install -r requirements.txt
```

### Make directories

For the webapp, make the following directories

```
mkdir webapp/postgres_data
mkdir webapp/import_data
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

Copy to the webapp/import_data directory for webapp use.

```
cp unzip device-510k-0001-of-0001.json webapp/import_data
cp unzip device-recall-0001-of-0001.json webapp/import_data
```

# Problems with the data

* Only a statement is available, not a summary
* A summary should be available, but wasn't on the website
* No predicate device is given in the summary
* A predicate device is in the summary, but it has no 510k entry
* A predicate device is in the summary, but it refers to a trade name and can't be traced back to 510k

# How to use manual_check.py

Install the dependencies with `pip3 install -r requirements.txt`

Then run `python3 manual_check.py`

This should open a PDF and prompt you for input:

> Enter a predicate ID for K040346, or press F to finish inputting predicates for this device. Press S if no predicates can be found.


The PDFs shown in this prompt were flagged as missing a predicate device from the automatic scraping process.
Sometimes there may legitimately be no predicate. For example latex gloves are specifically regulated by
[21 CFR 880.6250](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/cfrsearch.cfm?fr=880.6250),
and don't need a predicate device.

These can be skipped by entering "S" into the prompt.

Sometimes the summary will just give some generic statement like:

> The subject device is substantially equivalent to similar previously cleared devices.

These can also be skipped.

When a summary does list a predicate (or predicates), it will either be by device name, or K number.
If the K number is available, just type it into the prompt.

If it's not available, you'll need to search for device name on the
[FDA website](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm).

Sometimes these names will not have an exact match, so you may need to search by
product code, applicant name, or a subset of the listed name provided to get a match.

When a device has multiple predicates, you can enter them one at a time. Once you are done,
enter "F" to move on to the next device.

## Challenges finding devices by name

### Finding a match by name

Sometimes it can be difficult to find devices in the 510k Database by name.
The device name doesn't always match exactly with the name provided in the PDF.

Usually I'll just pick a few distinctive words to search on from the name, rather than providing all of them.
The name field doesn't search in order, and it looks for superstrings of each word provided.
This means that it's better to search on the distinctive parts of the word to find a match.

Sometimes the database name contains typos which will cause a search to fail.
For example, the device named [Zenith Flowable Deposit](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K970683)
is spelled "Zenih". Because the search field uses exact matching, a search for "Zenith" will not reveal this device.
I found it by searching for "flowable composite" and then ctrl + f ing the page for "zen".

Search is not case-sensitive, so you can just type in lowercase.

When searching for punctuation, I usually replace it with a space. For example, searching 
for a device named "flo-fil" from a PDF, I will search for "flo fil".
This will match other possible formats like "flofil" or "flo fil"

### Disambiguating devices

Sometimes a device name will have many submissions. I usually just pick the earliest one one available.
An important note: you must check the decision date of the device used. If the date is prior to the decision
of the PDF you're looking at, it can't be used (because they cannot have considered this a predicate yet).

### Confusion over applicant names

Sometimes an applicant will be an individual working at a company, or may be the company itself.
Sometimes the company name doesn't match the PDF, because there was an acquisition or merger.
Generally I just go by the trade name of the device, rather than requiring the applicant to match 100%.