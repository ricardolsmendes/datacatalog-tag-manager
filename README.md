# datacatalog-tag-manager

A Python package to manage Google Cloud Data Catalog tags, loading metadata from external sources.
Currently supports the CSV file format.

[![license](https://img.shields.io/github/license/ricardolsmendes/datacatalog-tag-manager.svg)](https://github.com/ricardolsmendes/datacatalog-tag-manager/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/datacatalog-tag-manager.svg)](https://pypi.org/project/datacatalog-tag-manager)
[![issues](https://img.shields.io/github/issues/ricardolsmendes/datacatalog-tag-manager.svg)](https://github.com/ricardolsmendes/datacatalog-tag-manager/issues)
[![continuous integration](https://github.com/ricardolsmendes/datacatalog-tag-manager/actions/workflows/continuous-integration.yaml/badge.svg)](https://github.com/ricardolsmendes/datacatalog-tag-manager/actions/workflows/continuous-integration.yaml)
[![continuous delivery](https://github.com/ricardolsmendes/datacatalog-tag-manager/actions/workflows/continuous-delivery.yaml/badge.svg)](https://github.com/ricardolsmendes/datacatalog-tag-manager/actions/workflows/continuous-delivery.yaml)

<!--
  DO NOT UPDATE THE TABLE OF CONTENTS MANUALLY
  run `npx markdown-toc -i README.md`.

  Please stick to 100-character line wraps as much as you can.
-->

## Table of Contents

<!-- toc -->

- [1. Environment setup](#1-environment-setup)
  * [1.1. Python + virtualenv](#11-python--virtualenv)
    + [1.1.1. Install Python 3.6+](#111-install-python-36)
    + [1.1.2. Create a folder](#112-create-a-folder)
    + [1.1.3. Create and activate an isolated Python environment](#113-create-and-activate-an-isolated-python-environment)
    + [1.1.4. Install the package](#114-install-the-package)
  * [1.2. Docker](#12-docker)
    + [1.2.1. Get the source code](#121-get-the-source-code)
  * [1.3. Auth credentials](#13-auth-credentials)
    + [1.3.1. Create a service account and grant it below roles](#131-create-a-service-account-and-grant-it-below-roles)
    + [1.3.2. Download a JSON key and save it as](#132-download-a-json-key-and-save-it-as)
    + [1.3.3. Set the environment variables](#133-set-the-environment-variables)
- [2. Manage Tags](#2-manage-tags)
  * [2.1. Create or Update](#21-create-or-update)
    + [2.1.1. From a CSV file](#211-from-a-csv-file)
  * [2.2. Delete](#22-delete)
    + [2.2.1. From a CSV file](#221-from-a-csv-file)
- [3. How to contribute](#3-how-to-contribute)
  * [3.1. Report Issues](#31-report-issues)
  * [3.2. Contribute code](#32-contribute-code)

<!-- tocstop -->

---

## 1. Environment setup

### 1.1. Python + virtualenv

Using [virtualenv][1] is optional, but strongly recommended unless you use [Docker](#12-docker).

#### 1.1.1. Install Python 3.6+

#### 1.1.2. Create a folder

This is recommended so all related stuff will reside at same place, making it easier to follow
below instructions.

```sh
mkdir ./datacatalog-tag-manager
cd ./datacatalog-tag-manager
```

_All paths starting with `./` in the next steps are relative to the `datacatalog-tag-manager`
folder._

#### 1.1.3. Create and activate an isolated Python environment

```sh
pip install --upgrade virtualenv
python3 -m virtualenv --python python3 env
source ./env/bin/activate
```

#### 1.1.4. Install the package

```sh
pip install --upgrade datacatalog-tag-manager
```

### 1.2. Docker

_Docker_ may be used as an option to run `datacatalog-tag-manager`. In this case, please disregard
the [above](#11-python--virtualenv) _virtualenv_ setup instructions.

#### 1.2.1. Get the source code

```sh
git clone https://github.com/ricardolsmendes/datacatalog-tag-manager
cd ./datacatalog-tag-manager
```

### 1.3. Auth credentials

#### 1.3.1. Create a service account and grant it below roles

- `BigQuery Metadata Viewer`
- `Data Catalog TagTemplate User`
- A custom role with `bigquery.datasets.updateTag` and `bigquery.tables.updateTag` permissions

#### 1.3.2. Download a JSON key and save it as

- `./credentials/datacatalog-tag-manager.json`

#### 1.3.3. Set the environment variables

_This step may be skipped if you're using [Docker](#12-docker)._

```sh
export GOOGLE_APPLICATION_CREDENTIALS=./credentials/datacatalog-tag-manager.json
```

## 2. Manage Tags

### 2.1. Create or Update

#### 2.1.1. From a CSV file

- _SCHEMA_

The metadata schema to create or update Tags is presented below. Use as many lines as needed to
describe all the Tags and Fields you need.

| Column                            | Description                                                                                                                 | Mandatory |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | :-------: |
| **linked_resource OR entry_name** | Full name of the BigQuery or PubSub asset the Entry refers to, or an Entry name if you are working with [Custom Entries][2] |  &check;  |
| **template_name**                 | Resource name of the Tag Template for the Tag                                                                               |  &check;  |
| **column**                        | Attach Tags to a column belonging to the Entry schema                                                                       |  &cross;  |
| **field_id**                      | Id of the Tag field                                                                                                         |  &check;  |
| **field_value**                   | Value of the Tag field                                                                                                      |  &check;  |

- _SAMPLE INPUT_

1. [sample-input/upsert-tags][3] for reference;
1. [Data Catalog Sample Tags][5] (Google Sheets) might help to create/export a CSV file.

- _COMMANDS_

**Python + virtualenv**

```sh
datacatalog-tags upsert --csv-file <CSV-FILE-PATH>
```

**Docker**

```sh
docker build --rm --tag datacatalog-tag-manager .
docker run --rm --tty \
  --volume <CREDENTIALS-FILE-FOLDER>:/credentials --volume <CSV-FILE-FOLDER>:/data \
  datacatalog-tag-manager upsert --csv-file /data/<CSV-FILE-PATH>
```

### 2.2. Delete

#### 2.2.1. From a CSV file

- _SCHEMA_

The metadata schema to delete Tags is presented below. Use as many lines as needed to delete all
the Tags you want.

| Column                            | Description                                                                                                                 | Mandatory |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | :-------: |
| **linked_resource OR entry_name** | Full name of the BigQuery or PubSub asset the Entry refers to, or an Entry name if you are working with [Custom Entries][2] |  &check;  |
| **template_name**                 | Resource name of the Tag Template of the Tag                                                                                |  &check;  |
| **column**                        | Delete Tags from a column belonging to the Entry schema                                                                     |  &cross;  |

- _SAMPLE INPUT_

1. [sample-input/delete-tags][4] for reference;
1. [Data Catalog Sample Tags][5] (Google Sheets) might help to create/export a CSV file.

- _COMMANDS_

**Python + virtualenv**

```sh
datacatalog-tags delete --csv-file <CSV-FILE-PATH>
```

**Docker**

```sh
docker build --rm --tag datacatalog-tag-manager .
docker run --rm --tty \
  --volume <CREDENTIALS-FILE-FOLDER>:/credentials --volume <CSV-FILE-FOLDER>:/data \
  datacatalog-tag-manager delete --csv-file /data/<CSV-FILE-PATH>
```

## 3. How to contribute

Please make sure to take a moment and read the [Code of
Conduct](https://github.com/ricardolsmendes/datacatalog-tag-manager/blob/master/.github/CODE_OF_CONDUCT.md).

### 3.1. Report Issues

Please report bugs and suggest features via the [GitHub
Issues](https://github.com/ricardolsmendes/datacatalog-tag-manager/issues).

Before opening an issue, search the tracker for possible duplicates. If you find a duplicate, please
add a comment saying that you encountered the problem as well.

### 3.2. Contribute code

Please make sure to read the [Contributing
Guide](github.com/ricardolsmendes/datacatalog-tag-manager/blob/master/.github/CONTRIBUTING.md)
before making a pull request.

[1]: https://virtualenv.pypa.io/en/latest/
[2]: https://cloud.google.com/data-catalog/docs/how-to/custom-entries
[3]: https://github.com/ricardolsmendes/datacatalog-tag-manager/tree/master/sample-input/upsert-tags
[4]: https://github.com/ricardolsmendes/datacatalog-tag-manager/tree/master/sample-input/delete-tags
[5]: https://docs.google.com/spreadsheets/d/1bqeAXjLHUq0bydRZj9YBhdlDtuu863nwirx8t4EP_CQ
