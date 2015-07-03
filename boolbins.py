#!/usr/bin/env python

import argparse
import os.path
import csv
import logging
import collections
import contextlib


IGNORED_INITIAL_COLUMNS = ["Time", "Cell_length"]
IGNORED_INITIAL_COLUMNS_POSSIBILITY2 = ["Time: Time", "Event_length: Event_length"]

class BoolBinsException(Exception): pass


@contextlib.contextmanager
def safe_open_csv_file(file_name, minimum_columns=1):
    """Try to open the file as a csv. If there's only one column in the first row, then try to open as a tsv.
    It that still only has one column, throw an error."""
    with open(file_name, 'rU') as f:
        reader = csv.reader(f)
        if len(reader.next()) > minimum_columns:
            f.seek(0)
            yield reader
            return
        f.seek(0)
        reader = csv.reader(f, delimiter="\t")
        if len(reader.next()) > minimum_columns:
            f.seek(0)
            yield reader
            return
    raise BoolBinsException("Error opening csv file %s, neither comma nor tab separated" % file_name)


def get_frequencies_for_file(file_name, thresholds, limit):
    logging.debug("\n")
    logging.info("Processing file %s", file_name)

    with safe_open_csv_file(file_name) as reader:
        header = reader.next()
        frequencies = collections.defaultdict(float)
        total_cells = processed_cells = 0

        for row in reader:
            total_cells += 1
            if limit == 0 or total_cells <= limit:
                processed_cells += 1
                headers_above_threshold = set()
                for i in xrange(len(IGNORED_INITIAL_COLUMNS), len(header)):
                    if header[i] in thresholds and float(row[i]) > thresholds[header[i]]:
                        headers_above_threshold.add(header[i])
                # Note, the empty set represents null cells
                frequencies[frozenset(headers_above_threshold)] += 1

    for header, count in frequencies.iteritems():
        frequencies[header] = count * 1.0 / processed_cells

    if limit == 0:
        logging.info("File had: %s cells" % total_cells)
    else:
        logging.info("File had: %s cells. Limited to first %s" % (total_cells, limit))
    logging.debug("Antibody frequencies:")
    for headers, freq in frequencies.iteritems():
        logging.debug("    %s: %s" % (headers, freq))

    return frequencies


def calculate_diversity(frequencies_by_header):
    return 1.0 / sum([i*i for i in frequencies_by_header.values()])


def make_pretty_name_for_bin_combo(combo):
    # each item in combo is like set("(Cd110)Dd: HLADR", "(Ce140)Dd: beads")
    if not combo:
        # The null cell
        return "[]"
    return " ".join(sorted([i.split(" ")[-1] for i in combo]))


def process_files(file_names, thresholds, output_file_name, limit, diversity):
    frequencies_by_file = {f: get_frequencies_for_file(f, thresholds, limit) for f in file_names}

    # This is the set of all possible antibody combinations that are above the threshold on a cell.
    # ie. a set of sets of headers
    all_possible_bin_combos = set()
    for _, frequencies in frequencies_by_file.iteritems():
        all_possible_bin_combos |= set(frequencies.keys())
    all_possible_bin_combos = list(all_possible_bin_combos)
    all_possible_bin_combos.sort(key=lambda x: (len(x), x))
    logging.debug("Got %s possible antibody combinations: %s" % (len(all_possible_bin_combos), all_possible_bin_combos))

    files = frequencies_by_file.keys()
    files.sort()
    with open(output_file_name, 'w') as output:
        w = csv.writer(output)

        # Write out the first header row
        w.writerow([""] + files)

        # Write out a row for each other combo of antibodies
        for combo in all_possible_bin_combos:
            row = [make_pretty_name_for_bin_combo(combo)]
            for f in files:
                row.append(frequencies_by_file[f].get(combo, 0))
            w.writerow(row)

    # Output diversity scores
    if diversity:
        with open(diversity, 'w') as output:
            w = csv.writer(output)
            w.writerow(["File", "Diversity"])
            for f in files:
                w.writerow([f, calculate_diversity(frequencies_by_file[f])])


def discover_all_files(headers, files_or_directories):
    all_valid_files = []
    while len(files_or_directories) > 0:
        f = files_or_directories.pop()
        if os.path.isdir(f):
            files_or_directories += [os.path.join(f, i) for i in os.listdir(f)]
        elif f.endswith(".txt") or f.endswith(".csv"):
            with safe_open_csv_file(f) as r:
                header_line = r.next()
            if header_line == headers:
                all_valid_files.append(f)
            else:
                logging.warning("Ignoring file %s, headers don't match the thresholds file" % f)
        else:
            logging.warning("Ignoring %s, not a csv or txt file" % f)
    logging.info("Got %s files to process:" % len(all_valid_files))
    for f in all_valid_files:
        logging.debug("    %s" % f)
    return all_valid_files


def get_thresholds_from_file(file_name):
    with safe_open_csv_file(file_name) as reader:
        headers = reader.next()
        thresholds = reader.next()
        to_include = reader.next()

    if headers[:len(IGNORED_INITIAL_COLUMNS)] != IGNORED_INITIAL_COLUMNS & 
       headers[:len(IGNORED_INITIAL_COLUMNS)] != IGNORED_INITIAL_COLUMNS_POSSIBILITY2:
        raise BoolBinsException("Badly formatted thresholds file. Needs initial headers: %s" % IGNORED_INITIAL_COLUMNS)

    if len(headers) != len(thresholds) or len(headers) != len(to_include):
        raise BoolBinsException("Invalid threshold file, the headers (%s), thresholds (%s), and inclusions (%s) row lengths don't match" % (
            len(headers), len(thresholds), len(to_include)))

    thresholds_per_header = {}
    for i in xrange(len(IGNORED_INITIAL_COLUMNS), len(headers)):
        if to_include[i].lower().strip() in ["true", "yes", "1", "t"]:
            try:
                thresholds_per_header[headers[i]] = float(thresholds[i])
            except ValueError as e:
                raise BoolBinsException("Bad threshold for column %s (%s), could not convert threshold to number: '%s'" % (i, headers[i], thresholds[i]))

    logging.info("Loaded %s thresholds" % len(thresholds_per_header))
    return headers, thresholds_per_header


def run(threshold_file_name, file_names, output_file_name, limit, diversity):
    headers, thresholds = get_thresholds_from_file(threshold_file_name)
    logging.debug("Got thresholds: %s" % thresholds)
    process_files(discover_all_files(headers, file_names), thresholds, output_file_name, limit, diversity)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Performs boolean gating on flow cytometry data')
    parser.add_argument('-t', '--thresholds', type=str, required=True, help='File with the thresholds to use for each antibody')
    parser.add_argument('-o', '--output', type=str, default="output.csv", help='File to output the data to')
    parser.add_argument('-v', '--verbose', action="store_true", help='Show debug logging')
    parser.add_argument('-l', '--limit', type=int, default=0, help='Process the first `limit` lines of each file, 0 (default) for all of them.')
    parser.add_argument('-d', '--diversity', type=str, default="", help='If given, output diversity scores to this file')
    parser.add_argument('files', metavar='file', type=str, nargs='+', help='Files or directories to process')

    args = parser.parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)
    try:
        run(args.thresholds, args.files, args.output, args.limit, args.diversity.strip())
    except BoolBinsException as e:
        logging.error("%s" % e)
