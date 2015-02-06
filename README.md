# OncoPy
## A Python Framework and API for Cancer Genomics

OncoPy is a Python package that serves to provide a framework and API for handling and storing cancer genomics data and metadata. Essentially, OncoPy consists of a set of Python classes that serve to model entities encountered in cancer genomics research. This includes patients, samples, various mutation types and the effects of these mutations, just to name a few. 

Moreover, these models are built upon SQLAlchemy, which readily enables the use of a database backend to store all of this data and metadata. Much of the relationships between various entities (_e.g._ samples relating to a patient, effects relating to a mutation) are already handled by OncoPy such that the user doesn't have to.

The OncoPy framework and API is designed to be easy to use. To get started with a database, you simply connect, create your tables and you're ready to populate your database. Assuming a `parse_vcf` function that creates a dictionary of key-value pairs corresponding to the parameters of the `oncopy.SingleNucleotideVariant` class, the following code shows how SNVs could easily be stored in a MySQL database. And soon, a VCF file parser will no longer be necessary (see Future Plans below). 

```python
import oncopy
oncopy.connect(MysqlConnection(
    host="localhost", 
    user="oncopyfan", 
    password="oncopyrocks!", 
    database="cancer_project"))
for line in vcf_file:
    row_dict = parse_vcf(line)
    snv = oncopy.SingleNucleotideVariant(**row_dict)
    snv.save()
```

Additionally, an assortment of scripts that make use of the OncoPy framework and API are provided as part of this repository in `bin`. These can perform a variety of tasks, such as populating the database with reference annotations (_e.g._ genes, transcripts, etc.).

## Future Plans

OncoPy will be expanded to include classes for handling common (and also uncommon) file types. These will utilize the models described above in order to allow easy conversion from one file format to another as well as ready-made file parsing for creating a list of OncoPy entities (_e.g._ genes, mutations, etc.) and optionally loading these into a database. 
