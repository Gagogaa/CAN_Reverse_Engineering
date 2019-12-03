# TODO Maybe have make model year at the command line for now

import argparse
import re
from pathlib import Path

from FileBoi import FileBoi
from Sample import Sample

_DESCRIPTION = '''
'''

_VERSION = '0.0.1'


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = _DESCRIPTION)

    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-O", "--output-dir", help="output directory for figures and charts", default=".")
    parser.add_argument("-I", "--input-files", help="list of input files", nargs='+', default=None, required=True)
    parser.add_argument("-K", "--kfold-n", help="", type=int, default=5)

    args = parser.parse_args()

    if args.version:
        print(_VERSION)
        exit()

    samples = []

    if args.input_files is None:
        # TODO print help info
        exit()
    else:
        for file_index, file in enumerate(args.input_files):
            if re.match('.*\.log', file):
                # filenames using ../../ and the like are really troublesome here
                print('input file: ' + file)
                print('abs input file: ' + str(Path(file).resolve()))
                samples.append(Sample(make="",
                                      model="",
                                      year="",
                                      sample_number=file_index,
                                      sample_path=str(Path(file).resolve()),
                                      kfold_n=args.kfold_n))


    # Cross validation parameters for finding an optimal tokenization inversion distance threshold -- NOT WORKING?
    current_vehicle_number = 0

    # Okay so it does the computation twice?? What the fuck
    # good_boi = FileBoi()
    # samples = good_boi.go_fetch(args.kfold_n)

    # for key, sample_list in samples.items():  # type: tuple, list
    for sample in samples:  # type: Sample
        # TODO This if for each car then?
        # print(current_vehicle_number)
        print("\nData import and Pre-Processing for " + sample.output_vehicle_dir)
        id_dict, j1979_dict, pid_dict = sample.pre_process()
        if j1979_dict:
            sample.plot_j1979(j1979_dict, vehicle_number=str(current_vehicle_number))

        #                 LEXICAL ANALYSIS                     #
        print("\n\t##### BEGINNING LEXICAL ANALYSIS OF " + sample.output_vehicle_dir + " #####")
        sample.tokenize_dictionary(id_dict)
        signal_dict = sample.generate_signals(id_dict, bool(j1979_dict))
        sample.plot_arb_ids(id_dict, signal_dict, vehicle_number=str(current_vehicle_number))

        #                 LEXICAL ANALYSIS                     #
        print("\n\t##### BEGINNING SEMANTIC ANALYSIS OF " + sample.output_vehicle_dir + " #####")
        corr_matrix, combined_df = sample.generate_correlation_matrix(signal_dict)
        if j1979_dict:
            signal_dict, j1979_correlation = sample.j1979_labeling(j1979_dict, signal_dict, combined_df)
        cluster_dict, linkage_matrix = sample.cluster_signals(corr_matrix)
        sample.plot_clusters(cluster_dict, signal_dict, bool(j1979_dict), vehicle_number=str(current_vehicle_number))
        sample.plot_dendrogram(linkage_matrix, vehicle_number=str(current_vehicle_number))
        # current_vehicle_number += 1
