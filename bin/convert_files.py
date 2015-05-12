#!/us/bin/env python

"""
convert_file.py
===============
This script takes in any cancer_api-supported file type
and converts it to another supported file type.

Inputs:
- Input file(s)
- cancer_api input file type
- cancer_api parser
- cancer_api output file type
- Output directory (optional)

Output:
- Converted file(s)
"""

import argparse
import os
import cancer_api


def main():

    # ========================================================================================== #
    # Argument parsing
    # ========================================================================================== #

    parser = argparse.ArgumentParser(description="Convert between different file types.")
    parser.add_argument("input_type", nargs=1, help="cancer_api file type for input file(s)")
    parser.add_argument("input_parser", nargs=1, help="cancer_api parser for input file")
    parser.add_argument("output_type", nargs=1, help="cancer_api file type for output file")
    parser.add_argument("input_files", nargs="+", help="List of input file(s) (same type)")
    parser.add_argument("--output_dir", help="Output all converted files in this directory")
    args = parser.parse_args()

    # ========================================================================================== #
    # Set up variables
    # ========================================================================================== #

    # Retrieve cancer_api objects for file type and parser
    input_type = getattr(cancer_api, args.input_type[0], None)
    input_parser = getattr(cancer_api, args.input_parser[0], None)
    output_type = getattr(cancer_api, args.output_type[0], None)
    if input_type is None or input_parser is None or output_type is None:
        raise ValueError("Unsupported file type or parser. Check `cancer_api` for supported "
                         "file types (`files` submodule) and parsers (`parsers` submodule).")

    # If output_dir is given, make sure it exists
    if args.output_dir and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    # ========================================================================================== #
    # Call convert_file()
    # ========================================================================================== #

    for infile in args.input_files:
        if args.output_dir:
            output_dir = args.output_dir
        else:
            output_dir = os.path.dirname(infile)
        convert_file(input_type, input_parser, output_type, infile, output_dir)


def convert_file(intype, inparser, outtype, infile, outdir):
    """Convert file from one cancer_api-supported type to another"""
    opened_infile = intype.open(infile, parser_cls=inparser)
    root, ext = opened_infile.split_filename()
    outfilepath = os.path.join(outdir, "{}.{}".format(root, outtype.get_file_extension()))
    opened_outfile = outtype.convert(outfilepath, opened_infile)
    opened_outfile.write()


if __name__ == '__main__':
    main()
