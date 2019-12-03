# TODO Maybe have make model year at the command line for now

import argparse
import re
from pathlib import Path
from os import chdir, mkdir, path

from Sample import Sample

_DESCRIPTION = '''
'''

_VERSION = '0.0.1'


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = _DESCRIPTION)

    parser.add_argument("--version", "-V", help="show program version", action="store_true")
    parser.add_argument("--output-dir", "-O", help="output directory for figures and charts", default=".")
    parser.add_argument("--input-files", "-I", help="list of input files", nargs='+', default=None, required=True)
    parser.add_argument("--vehicle-name", help="name of the vehicle", type=str, default="") # TODO change the called code to respond to when this is None
    parser.add_argument("--kfold-n", "-K", help="", type=int, default=5)

    args = parser.parse_args()

    if args.version:
        print(_VERSION)
        exit()

    input_files = []

    if args.input_files is None:
        # TODO print help info
        exit()
    else:
        for file in args.input_files:
            if re.match('.*\.log', file):
                input_files.append(str(Path(file).resolve()))

    if not path.isdir(args.output_dir):
        mkdir(args.output_dir)

    chdir(args.output_dir)

    samples = []

    for file_index, file in enumerate(input_files):
        print('Reading sample ' + file)
        samples.append(Sample(make="",
                              model="",
                              year="",
                              sample_number=file_index,
                              sample_path=file,
                              kfold_n=args.kfold_n))

    try:
        # TODO This comment came with the original code I'm wondering if it means that the Validation step later in the process is not working
        # Cross validation parameters for finding an optimal tokenization inversion distance threshold -- NOT WORKING?
        for sample in samples:
            print("\nData import and Pre-Processing for " + sample.output_vehicle_dir)
            id_dict, j1979_dict, pid_dict = sample.pre_process()
            if j1979_dict:
                sample.plot_j1979(j1979_dict, vehicle_number=args.vehicle_name)

            #                 LEXICAL ANALYSIS                     #
            print("\n\t##### BEGINNING LEXICAL ANALYSIS OF " + sample.output_vehicle_dir + " #####")
            sample.tokenize_dictionary(id_dict)
            signal_dict = sample.generate_signals(id_dict, bool(j1979_dict))
            sample.plot_arb_ids(id_dict, signal_dict, vehicle_number=args.vehicle_name)

            #                 LEXICAL ANALYSIS                     #
            print("\n\t##### BEGINNING SEMANTIC ANALYSIS OF " + sample.output_vehicle_dir + " #####")
            corr_matrix, combined_df = sample.generate_correlation_matrix(signal_dict)
            if j1979_dict:
                signal_dict, j1979_correlation = sample.j1979_labeling(j1979_dict, signal_dict, combined_df)
            cluster_dict, linkage_matrix = sample.cluster_signals(corr_matrix)
            sample.plot_clusters(cluster_dict, signal_dict, bool(j1979_dict), vehicle_number=args.vehicle_name)
            sample.plot_dendrogram(linkage_matrix, vehicle_number=args.vehicle_name)
    except KeyboardInterrupt:
        print("Keyboard interupt pressed program quit")
