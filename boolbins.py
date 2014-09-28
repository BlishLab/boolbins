import argparse
import os.path
import csv
import logging
import collections


IGNORED_INITIAL_COLUMN_COUNT = 2


def get_frequencies_for_file(fileName, thresholds):
    logging.debug("\n")
    logging.debug("Processing file %s", fileName)
    reader = csv.reader(open(fileName, 'rU'))
    header = reader.next()
    frequencies = collections.defaultdict(float)
    total_cells = 0

    for row in reader:
        total_cells += 1
        headers_above_threshold = set()
        for i in xrange(IGNORED_INITIAL_COLUMN_COUNT, len(header)):
            if header[i] in thresholds and float(row[i]) >= thresholds[header[i]]:
                headers_above_threshold.add(header[i])
        if headers_above_threshold:
            frequencies[frozenset(headers_above_threshold)] += 1

    for header, count in frequencies.iteritems():
        frequencies[header] = count * 1.0 / total_cells

    logging.debug("File had: %s cells with overall frequencies:" % total_cells)
    for headers, freq in frequencies.iteritems():
        logging.debug("    %s: %s" % (headers, freq))

    return frequencies


def make_pretty_name_for_bin_combo(combo):
    return " ".join(sorted(list(combo)))


def process_files(file_names, thresholds, output_file_name):
    frequencies_by_file = {f: get_frequencies_for_file(f, thresholds) for f in file_names}

    # This is the set of all possible antibody combinations that are above the threshold on a cell. ie. a set of sets of headers
    all_possible_bin_combos = set()
    for _, frequencies in frequencies_by_file.iteritems():
        all_possible_bin_combos |= set(frequencies.keys())
    all_possible_bin_combos = list(all_possible_bin_combos)
    all_possible_bin_combos.sort()
    logging.debug("Got %s possible antibody combinations: %s" % (len(all_possible_bin_combos), all_possible_bin_combos))

    with open(output_file_name, 'w') as output:
        w = csv.writer(output)
        w.writerow(["Filename"] + [make_pretty_name_for_bin_combo(i) for i in all_possible_bin_combos])

        for f, frequencies in frequencies_by_file.iteritems():
            row = [f]
            for combo in all_possible_bin_combos:
                row.append(frequencies.get(combo, 0))
            w.writerow(row)


def discover_all_files(files_or_directories):
    all_valid_files = []
    while len(files_or_directories) > 0:
        f = files_or_directories.pop()
        if os.path.isdir(f):
            files_or_directories += [os.path.join(f, i) for i in os.listdir(f)]
        elif f.endswith(".txt") or f.endswith(".csv"):
            all_valid_files.append(f)
        else:
            logging.debug("Ignoring %s" % f)
    logging.debug("Got %s files to process:" % len(all_valid_files))
    for f in all_valid_files:
        logging.debug("    %s" % f)
    return all_valid_files


def get_thresholds_from_file(f):
    reader = csv.reader(f)
    headers = reader.next()
    thresholds = reader.next()
    to_include = reader.next()
    if len(headers) != len(thresholds) or len(headers) != len(to_include):
        raise Exception("Invalid threshold file, the headers (%s), thresholds (%s), and inclusions (%s) row lengths don't match" % (
            len(headers), len(thresholds), len(to_include)))

    thresholds_per_header = {}
    for i in xrange(IGNORED_INITIAL_COLUMN_COUNT, len(headers)):
        if to_include[i].lower().strip() in ["true", "yes", "1", "t"]:
            thresholds_per_header[headers[i]] = float(thresholds[i])
    return thresholds_per_header


def run(threshold_file, file_names, output_file_name):
    thresholds = get_thresholds_from_file(threshold_file)
    logging.debug("Got thresholds: %s" % thresholds)
    process_files(discover_all_files(file_names), thresholds, output_file_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Performs boolean gating on flow cytometry data')
    parser.add_argument('--thresholds', type=file, required=True, help='File with the thresholds to use for each antibody')
    parser.add_argument('--output', type=str, default="output.csv", help='File to output the data to')
    parser.add_argument('--debug', action="store_true", help='Show debug logging')
    parser.add_argument('files', metavar='file', type=str, nargs='+', help='Files or directories to process')

    args = parser.parse_args()
    log_level = logging.DEBUG if args.debug else logging.WARNING
    logging.basicConfig(level=log_level)

    run(args.thresholds, args.files, args.output)
