#!/usr/bin/env python

"""
reference_data_loader.py
========================
This script downloads reference data from Ensembl and
loads it into the database. The concerned database tables
are: gene, transcript, exon, protein and protein_region.
The script downloads the data using Ensembl's BioMart XML
Query API.

Known Issues
------------
- The protein_region table isn't being loaded yet.
- Exons that only contain UTR regions are ignored.
- Currently, when the proteins are obtained from Ensembl,
    the vast majority of the results are transcripts
    without a protein ID. We should tweak the XML query
    in order to be more efficient and exclude these from
    the download.
"""

import argparse
import cancer_api
import os
import requests
from collections import defaultdict
import logging

BIOMART_API_URL = 'http://grch37.ensembl.org/biomart/martservice/'
GENE_FIELDNAMES = [
    'ensembl_gene_id', 'hgnc_symbol', 'gene_biotype', 'external_gene_name', 'chromosome_name',
    'start_position', 'end_position']
EXON_FIELDNAMES = [
    'ensembl_exon_id', 'ensembl_transcript_id', 'ensembl_gene_id', 'strand', 'phase',
    '5_utr_start', '5_utr_end', 'cdna_coding_start', 'cdna_coding_end', '3_utr_start',
    '3_utr_end', 'cds_start', 'cds_end', 'genomic_coding_start', 'genomic_coding_end',
    'exon_chrom_start', 'exon_chrom_end']
PROTEIN_FIELDNAMES = ['ensembl_peptide_id', 'ensembl_transcript_id', 'cds_length']


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description=('This script loads Ensembl reference data into the cancer database.'))
    parser.add_argument('db_host', help='Database server host')
    parser.add_argument('db_user', help='Database user')
    parser.add_argument('db_password', help='Password for user')
    parser.add_argument('db_name', help='Name of target database')
    parser.add_argument('--cache_dir', '-o', default='',
                        help='Directory for caching/reloading data')
    parser.add_argument('--fast_mode', '-f', action='store_true',
                        help='Disables check for preexisting entries, which is useful for '
                        'loading empty databases. Ensure that the input has no duplicates.')
    args = parser.parse_args()

    # Setup logging
    cancer_api.utils.setup_logging()
    logging.info('Initializing script...')

    # Establish connection with cancer_db instance
    logging.info('Connecting to cancer database...')
    db_cnx = cancer_api.connect(cancer_api.MysqlConnection(args.db_host, args.db_user,
                            args.db_password, args.db_name))
    db_session = db_cnx.session
    db_cnx.create_tables()

    # Create output directory if doesn't exist
    if not os.path.exists(args.cache_dir):
        logging.info('Creating output directory...')
        os.makedirs(args.cache_dir)
    else:
        logging.info('Output directory already exists. Will attempt to load data from cache.')

    # For gene table
    gene_cache_filename = os.path.join(
        args.cache_dir, 'ensembl_genes_78.homo_sapiens.GRCh37.tsv')
    # If cache_dir specified, check there first
    if args.cache_dir and os.path.exists(gene_cache_filename):
        logging.info('Loading gene data from cache...')
        with open(gene_cache_filename) as gene_cache:
            gene_data = gene_cache.read()
    # Otherwise, download data from Ensembl
    else:
        logging.info('Downloading gene data from Ensembl...')
        gene_data = query_biomart_api(BIOMART_API_URL, GENE_QUERY)
        # If the cache_dir was specified, but the data was downloaded,
        # cache the data
        if args.cache_dir:
            logging.info('Caching gene data in output directory...')
            with open(gene_cache_filename, 'w') as gene_cache:
                gene_cache.write(gene_data)
    # Load data in database
    logging.info('Loading gene data into database...')
    gene_counter = 0
    for row_dict in iter_data(gene_data, GENE_FIELDNAMES):
        # Each row_dict has the following keys (see GENE_FIELDNAMES)
        # 'ensembl_gene_id', 'hgnc_symbol', 'gene_biotype', 'external_gene_name',
        # 'chromosome_name', 'start_position', 'end_position'

        gene_dict = {
            'gene_ensembl_id': row_dict['ensembl_gene_id'],
            'gene_symbol': row_dict['hgnc_symbol'],
            'biotype': row_dict['gene_biotype'],
            'chrom': row_dict['chromosome_name'],
            'start_pos': row_dict['start_position'],
            'end_pos': row_dict['end_position'],
            'length': int(row_dict['end_position']) - int(row_dict['start_position']) + 1
        }
        if args.fast_mode:
            gene = cancer_api.Gene(**gene_dict)
            gene.add()
        else:
            cancer_api.Gene.get_or_create(**gene_dict)
        gene_counter += 1
    db_cnx.commit()
    logging.info('Finished loading {} genes into the database.'.format(gene_counter))

    # For transcript and exon tables
    exon_cache_filename = os.path.join(
        args.cache_dir, 'ensembl_transcripts_and_exons_78.homo_sapiens.GRCh37.tsv')
    # If cache_dir specified, check there first
    if args.cache_dir and os.path.exists(exon_cache_filename):
        logging.info('Loading transcript and exon data from cache...')
        with open(exon_cache_filename) as exon_cache:
            exon_data = exon_cache.read()
    # Otherwise, download data from Ensembl
    else:
        logging.info('Downloading transcript and exon data from Ensembl...')
        exon_data = query_biomart_api(BIOMART_API_URL, EXON_QUERY)
        # If the cache_dir was specified, but the data was downloaded,
        # cache the data
        if args.cache_dir:
            logging.info('Caching transcript and exon data in output directory...')
            with open(exon_cache_filename, 'w') as exon_cache:
                exon_cache.write(exon_data)
    # Load data in database
    logging.info('Loading transcript and exon data into database...')
    # Organize exons by transcript
    transcripts = defaultdict(lambda: {'exons': []})
    for row_dict in iter_data(exon_data, EXON_FIELDNAMES):
        # Each row_dict has the following keys (see EXON_FIELDNAMES):
        # 'ensembl_exon_id', 'ensembl_transcript_id', 'ensembl_gene_id', 'strand', 'phase',
        # '5_utr_start', '5_utr_end', 'cdna_coding_start', 'cdna_coding_end', '3_utr_start',
        # '3_utr_end', 'cds_start', 'cds_end', 'genomic_coding_start', 'genomic_coding_end',
        # 'exon_chrom_start', 'exon_chrom_end'

        # Add transcript info
        transcripts[row_dict['ensembl_transcript_id']].update({
            'transcript_ensembl_id': row_dict['ensembl_transcript_id'],
            'gene_ensembl_id': row_dict['ensembl_gene_id']
        })

        # Calculate some values for the exon depending on UTRs
        # Check if there's a UTR and if so, calculate its length
        # Also, calculate transcript start or end (incl. UTRs)
        utr_length = 0
        exon_length = int(row_dict['exon_chrom_end']) - int(row_dict['exon_chrom_start']) + 1
        # If there is a 5' UTR and coding region in the exon
        if row_dict['5_utr_start'] and row_dict['cdna_coding_start']:
            utr_length = int(row_dict['5_utr_end']) - int(row_dict['5_utr_start']) + 1
            transcript_start = int(row_dict['cdna_coding_start']) - utr_length
            transcript_end = int(row_dict['cdna_coding_end'])
            end_phase = str((int(row_dict['phase']) + exon_length) % 3)
        # If there is only a 5' UTR in the exon
        elif row_dict['5_utr_start'] and not row_dict['cdna_coding_start']:
            continue
        # If there is a coding region and a 3' UTR in the exon
        elif row_dict['3_utr_start'] and row_dict['cdna_coding_start']:
            utr_length = int(row_dict['3_utr_end']) - int(row_dict['3_utr_start']) + 1
            transcript_start = int(row_dict['cdna_coding_start'])
            transcript_end = int(row_dict['cdna_coding_end']) + utr_length
            end_phase = "-1"
        # If there is only a 3' UTR in the exon
        elif row_dict['3_utr_start'] and not row_dict['cdna_coding_start']:
            continue
        # If there is both a 5' UTR, a coding region and a 3' UTR in the exon
        elif (row_dict['5_utr_start'] and row_dict['3_utr_start'] and
                row_dict['cdna_coding_start']):
            utr5_length = int(row_dict['5_utr_end']) - int(row_dict['5_utr_start']) + 1
            utr3_length = int(row_dict['3_utr_end']) - int(row_dict['3_utr_start']) + 1
            transcript_start = int(row_dict['cdna_coding_start']) - utr5_length
            transcript_end = int(row_dict['cdna_coding_end']) + utr3_length
            end_phase = "-1"
        # If there is only a 5' UTR and 3' UTR in the exon
        elif (row_dict['5_utr_start'] and row_dict['3_utr_start'] and
                not row_dict['cdna_coding_start']):
            continue
        # If there is only a coding region
        elif (not row_dict['5_utr_start'] and not row_dict['3_utr_start'] and
                row_dict['cdna_coding_start']):
            transcript_start = int(row_dict['cdna_coding_start'])
            transcript_end = int(row_dict['cdna_coding_end'])
            end_phase = str((int(row_dict['phase']) + exon_length) % 3)
        # If there is no UTR and no coding region
        else:
            continue

        # Add exon to list of exons for transcript
        transcripts[row_dict['ensembl_transcript_id']]['exons'].append({
            'exon_ensembl_id': row_dict['ensembl_exon_id'],
            'strand': row_dict['strand'],
            'phase': row_dict['phase'],
            'end_phase': end_phase,
            'length': exon_length,
            'transcript_start_pos': transcript_start,
            'transcript_end_pos': transcript_end,
            'genome_start_pos': row_dict['exon_chrom_start'],
            'genome_end_pos': row_dict['exon_chrom_end'],
            'cdna_coding_start': row_dict['cdna_coding_start'],
            'cdna_coding_end': row_dict['cdna_coding_end']
        })
    # Now that all exons are organized by transcript,
    # iterate through transcripts, add transcript to database
    # and then add all its exons
    transcript_counter = 0
    all_exons = []
    for transcript_dict in transcripts.values():
        # Skip transcripts that contain no exons
        # (Probably because they didn't contain a coding region)
        if len(transcript_dict['exons']) == 0:
            continue
        # Obtain cds_start, cds_end and length from exons and then remove them from dict
        transcript_dict['cds_start_pos'] = min(
            [int(exon['cdna_coding_start']) for exon in transcript_dict['exons']])
        transcript_dict['cds_end_pos'] = max(
            [int(exon['cdna_coding_end']) for exon in transcript_dict['exons']])
        transcript_dict['length'] = sum(
            [int(exon['length']) for exon in transcript_dict['exons']])
        exons = transcript_dict.pop("exons")

        # Obtain gene ID for given gene Ensembl ID
        gene_ensembl_id = transcript_dict.pop("gene_ensembl_id")
        gene_id, = db_session.query(cancer_api.Gene.id).filter_by(
            gene_ensembl_id=gene_ensembl_id).first()
        transcript_dict["gene_id"] = gene_id

        # Add transcript to database
        if args.fast_mode:
            transcript = cancer_api.Transcript(**transcript_dict)
            transcript.add()
        else:
            transcript = cancer_api.Transcript.get_or_create(**transcript_dict)
        transcript_counter += 1

        for exon in exons:
            exon['transcript'] = transcript
            all_exons.append(exon)
    # Commit all transcripts in order to get IDs
    db_session.commit()
    # Iterate over all_exons and add them to database using transcript ID
    # Now that the transcripts have IDs
    exon_counter = 0
    for exon_dict in all_exons:
        exon_dict.pop("cdna_coding_start")
        exon_dict.pop("cdna_coding_end")
        transcript = exon_dict.pop("transcript")
        exon_dict["transcript_id"] = transcript.id
        exon_dict["gene_id"] = transcript.gene_id
        if args.fast_mode:
            exon = cancer_api.Exon(**exon_dict)
            exon.add()
        else:
            exon = cancer_api.Exon.get_or_create(**exon_dict)
        exon_counter += 1
    db_session.commit()
    logging.info('Finished loading {} transcripts into the database.'.format(transcript_counter))
    logging.info('Finished loading {} exons into the database.'.format(exon_counter))

    # For protein table
    protein_cache_filename = os.path.join(
        args.cache_dir, 'ensembl_proteins_78.homo_sapiens.GRCh37.tsv')
    # If cache_dir specified, check there first
    if args.cache_dir and os.path.exists(protein_cache_filename):
        logging.info('Loading gene data from cache...')
        with open(protein_cache_filename) as protein_cache:
            protein_data = protein_cache.read()
    # Otherwise, download data from Ensembl
    else:
        logging.info('Downloading protein data from Ensembl...')
        protein_data = query_biomart_api(BIOMART_API_URL, PROTEIN_QUERY)
    # If the cache_dir was specified, but the data was downloaded,
    # cache the data
        if args.cache_dir:
            logging.info('Caching protein data in output directory...')
            with open(protein_cache_filename, 'w') as protein_cache:
                protein_cache.write(protein_data)
    # Load data in database
    logging.info('Loading protein data into database...')
    protein_counter = 0
    for row_dict in iter_data(protein_data, PROTEIN_FIELDNAMES):
        # Only consider proteins with an Ensembl ID and length
        if row_dict['ensembl_peptide_id'] == '' or row_dict['cds_length'] == '':
            continue
        # Obtain related transcript
        transcript = db_session.query(cancer_api.Transcript).filter_by(
            transcript_ensembl_id=row_dict['ensembl_transcript_id']).first()
        transcript_id = transcript.id
        gene_id = transcript.gene_id
        protein_dict = {
            'protein_ensembl_id': row_dict['ensembl_peptide_id'],
            'cds_length': int(row_dict['cds_length']),
            'transcript_id': transcript_id,
            'gene_id': gene_id
        }
        if args.fast_mode:
            protein = cancer_api.Protein(**protein_dict)
            protein.add()
        else:
            protein = cancer_api.Protein.get_or_create(**protein_dict)
        protein_counter += 1
    db_session.commit()
    logging.info('Finished loading {} proteins into the database.'.format(protein_counter))

    # For protein_region table
    logging.warning('Did not load data into the protein_region table. Not implemented yet.')

    # Clean up
    db_cnx.close()
    logging.info('Finished loading Ensembl reference data into database.')


def query_biomart_api(biomart_url, xml_query):
    """Sends an XML query to a specified BioMart web service.
    Returns body of HTTP response.
    """
    response = requests.get(biomart_url, params={'query': xml_query})
    if response.status_code == 200:
        return response.text
    else:
        raise requests.exceptions.HTTPError(
            'Unsuccessful HTTP response (status code {}). Debug the following URL:\n{}'.format(
                response.status_code, response.url))


def iter_data(response, fieldnames):
    """Parses the BioMart data as a generator."""
    for line in response.split('\n'):
        # If line is empty, skip
        if line == '':
            continue
        row_dict = dict(zip(fieldnames, line.split('\t')))
        yield row_dict


GENE_QUERY = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "1"
        count = "" datasetConfigVersion = "0.6" >
    <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
        <Attribute name = "ensembl_gene_id" />
        <Attribute name = "hgnc_symbol" />
        <Attribute name = "gene_biotype" />
        <Attribute name = "external_gene_name" />
        <Attribute name = "chromosome_name" />
        <Attribute name = "start_position" />
        <Attribute name = "end_position" />
    </Dataset>
</Query>
"""


EXON_QUERY = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "1"
        count = "" datasetConfigVersion = "0.6" >
    <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
        <Attribute name = "ensembl_exon_id" />
        <Attribute name = "ensembl_transcript_id" />
        <Attribute name = "ensembl_gene_id" />
        <Attribute name = "strand" />
        <Attribute name = "phase" />
        <Attribute name = "5_utr_start" />
        <Attribute name = "5_utr_end" />
        <Attribute name = "cdna_coding_start" />
        <Attribute name = "cdna_coding_end" />
        <Attribute name = "3_utr_start" />
        <Attribute name = "3_utr_end" />
        <Attribute name = "cds_start" />
        <Attribute name = "cds_end" />
        <Attribute name = "genomic_coding_start" />
        <Attribute name = "genomic_coding_end" />
        <Attribute name = "exon_chrom_start" />
        <Attribute name = "exon_chrom_end" />
    </Dataset>
</Query>
"""


PROTEIN_QUERY = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Query>
<Query  virtualSchemaName = "default" formatter = "TSV" header = "0" uniqueRows = "1"
        count = "" datasetConfigVersion = "0.6" >
    <Dataset name = "hsapiens_gene_ensembl" interface = "default" >
        <Attribute name = "ensembl_peptide_id" />
        <Attribute name = "ensembl_transcript_id" />
        <Attribute name = "cds_length" />
    </Dataset>
</Query>
"""


if __name__ == '__main__':
    main()
