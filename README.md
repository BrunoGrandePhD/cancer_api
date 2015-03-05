# cancer_api
## A Python Framework and API for Cancer Genomics
[![Latest Version](https://img.shields.io/pypi/v/cancer-api.svg)](https://pypi.python.org/pypi/cancer-api/)
[![Build Status](https://travis-ci.org/brunogrande/cancer_api.svg?branch=master)](https://travis-ci.org/brunogrande/cancer_api)

cancer_api is a Python package that serves to provide a framework and API for handling and storing cancer genomics data and metadata. Essentially, this package consists of a set of Python classes that serve to model entities encountered in cancer genomics research. This includes patients, samples, various mutation types and the effects of these mutations, just to name a few. 

Moreover, these models are built upon SQLAlchemy, which readily enables the use of a database backend to store all of this data and metadata. Much of the relationships between various entities (_e.g._ samples relating to a patient, effects relating to a mutation) are already handled by cancer_api such that the user doesn't have to.

The cancer_api framework and API are designed to be easy to use. To get started with a database, you simply connect, create your tables and you're ready to populate your database. The following code shows how SNVs in a VCF file could easily be parsed and stored in a MySQL database in just a few lines. That's thanks to cancer_api's file parsers (work in progress). 

```python
import cancer_api
db = cancer_api.connect(MysqlConnection(
    host="localhost", 
    user="cancer_apifan", 
    password="cancer_apirocks!", 
    database="cancer_project"))
for snv in cancer_api.files.VcfFile(vcf_filepath):
    snv.add()
db.commit()
```

Additionally, an assortment of scripts that make use of the cancer_api framework and API are provided as part of this repository in `bin`. These can perform a variety of tasks, such as populating the database with reference annotations (_e.g._ genes, transcripts, etc.).

## Installation

### Dependencies

cancer_api's dependencies should be downloaded and installed automatically during the installation steps below. 

* `python>=2.7`
* `SQLAlchemy>=0.9.8`

### Installation Steps

To install cancer_api, simply run:

```bash
pip install cancer_api
```

## Release History

See [release history](HISTORY.md).
