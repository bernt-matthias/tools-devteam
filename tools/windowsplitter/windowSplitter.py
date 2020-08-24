#!/usr/bin/env python
"""
Split into windows.

usage: %prog input size out_file
   -l, --cols=N,N,N,N: Columns for chrom, start, end, strand in file
"""
from __future__ import print_function

import sys

from bx.cookbook import doc_optparse


# Default chrom, start, end, strand cols for a bed file
BED_DEFAULT_COLS = 0, 1, 2, 5


def parse_cols_arg(cols):
    """Parse a columns command line argument into a four-tuple"""
    if cols:
        # Handle case where no strand column included - in this case, cols
        # looks something like 1,2,3,
        if cols.endswith(','):
            cols += '0'
        col_list = [int(x) - 1 for x in cols.split(",")]
        return col_list
    else:
        return BED_DEFAULT_COLS


def main():
    # Parsing Command Line here
    options, args = doc_optparse.parse(__doc__)

    try:
        chr_col_1, start_col_1, end_col_1, strand_col_1 = parse_cols_arg(options.cols)
        inp_file, winsize, out_file, makesliding, offset = args
        winsize = int(winsize)
        offset = int(offset)
        makesliding = int(makesliding)
    except Exception:
        sys.exit("Data issue, click the pencil icon in the history item to correct the metadata attributes of the input dataset.")

    skipped_lines = 0
    first_invalid_line = 0
    invalid_line = None
    if offset == 0:
        makesliding = 0

    with open(out_file, 'w') as fo, open(inp_file) as fi:
        for i, line in enumerate(fi):
            line = line.strip()
            if line and line[0:1] != "#":
                try:
                    elems = line.split('\t')
                    start = int(elems[start_col_1])
                    end = int(elems[end_col_1])
                    if makesliding == 0:
                        numwin = (end - start) // winsize
                    else:
                        numwin = (end - start) // offset
                    if numwin > 0:
                        for _ in range(numwin):
                            elems_1 = elems
                            elems_1[start_col_1] = str(start)
                            elems_1[end_col_1] = str(start + winsize)
                            fo.write("%s\n" % '\t'.join(elems_1))
                            if makesliding == 0:
                                start = start + winsize
                            else:
                                start = start + offset
                                if start + winsize > end:
                                    break
                except Exception:
                    skipped_lines += 1
                    if not invalid_line:
                        first_invalid_line = i + 1
                        invalid_line = line

    if makesliding == 1:
        print('Window size=%d, Sliding=Yes, Offset=%d' % (winsize, offset))
    else:
        print('Window size=%d, Sliding=No' % (winsize))
    if skipped_lines > 0:
        print('Skipped %d invalid lines starting with #%d: "%s"' % (skipped_lines, first_invalid_line, invalid_line))


if __name__ == "__main__":
    main()
