# datacatalog-tag-manager

A Python package to manage Google Cloud Data Catalog tags, loading metadata from external sources.

[![CircleCI][1]][2]

## 1. Environment setup

### 1.1. Get the code

````bash
git clone https://github.com/ricardolsmendes/datacatalog-tag-manager
cd datacatalog-tag-manager
````

### 1.2. Auth credentials

##### 1.2.1. Create a service account and grant it below roles

- BigQuery Metadata Viewer
- Data Catalog TagTemplate User
- A custom role with `bigquery.datasets.updateTag` and `bigquery.tables.updateTag` permissions 

##### 1.2.2. Download a JSON key and save it as
- `./credentials/datacatalog-tag-manager.json`

### 1.3. Virtualenv

Using *virtualenv* is optional, but strongly recommended unless you use [Docker](#14-docker).

##### 1.3.1. Install Python 3.6+

##### 1.3.2. Create and activate an isolated Python environment

```bash
pip install --upgrade virtualenv
python3 -m virtualenv --python python3 env
source ./env/bin/activate
```

##### 1.3.3. Install the dependencies

```bash
pip install --upgrade --editable .
```

##### 1.3.4. Set environment variables

```bash
export GOOGLE_APPLICATION_CREDENTIALS=./credentials/datacatalog-tag-manager.json
```

### 1.4. Docker

Docker may be used as an alternative to run all the scripts. In this case, please disregard the
[Virtualenv](#13-virtualenv) install instructions.

## 2. Load Tags from CSV file

### 2.1. Create a CSV file representing the Tags to be created

Tags are composed by as many lines as required to represent all of their fields. The columns are
described as follows:

| Column              | Description                                        | Mandatory |
| ---                 | ---                                                | ---       |
| **linked_resource** | Full name of the asset the Entry refers to.        | Y         |
| **template_name**   | Resource name of the Tag Template for the Tag.     | Y         |
| **column**          | Attach Tags to a column belonging to Entry schema. | N         |
| **field_id**        | Name of the Tag field.                             | Y         |
| **field_value**     | Value of the Tag field.                            | Y         |

*TIPS* 
- *`sample-input/create-tags` for reference;*
- [Data Catalog Sample Tags][3] may help to create/export the CSV.

### 2.2. python main.py create-tags

- python

```bash
python main.py create-tags --csv-file CSV_FILE_PATH
```

- docker

```bash
docker build --rm --tag datacatalog-tag-manager .
docker run --rm --tty \
  -v ./credentials:/credentials -v CSV_FILE_FOLDER:/data \
  datacatalog-tag-manager create-tags --csv-file /data/CSV_FILE_NAME
```

[1]: https://circleci.com/gh/ricardolsmendes/datacatalog-tag-manager.svg?style=svg
[2]: https://circleci.com/gh/ricardolsmendes/datacatalog-tag-manager
[3]: https://docs.google.com/spreadsheets/d/1bqeAXjLHUq0bydRZj9YBhdlDtuu863nwirx8t4EP_CQ
