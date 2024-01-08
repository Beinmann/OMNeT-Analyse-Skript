import argparse
import math


def parse_args():
    parser = argparse.ArgumentParser(description="Script for analysing result (.vec) files and calculating quantile estimates as well as confidence intervals using the min-max and standard method")
    parser.add_argument(
        "--indipendent-replications",
        "-r",
        type=int,
        help="<int> number of indipendent replications to use"
    )
    parser.add_argument(
        "--do-calculate-standard-confidence-interval",
        type=str,
        help='<outfile_suffix> Calculate the standard method confidence "+ \
                "interval and add it to the outfile'
    )
    parser.add_argument(
        "--do-estimate-quantile",
        type=str,
        help='<outfile_suffix> Calculate an overall quantile estimate ' +
             'and add it to the outfile'
    )
    parser.add_argument(
        "--do-calculate-min-max-confidence-interval",
        type=str,
        help='<outfile_suffix> Calculate min max confidence interval ' +
             'for the data and write it to the outfile'
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        help="<int> batch size for the batch means method"
    )
    parser.add_argument(
        "--steady-state-starting-time",
        "-s",
        type=float,
        help="<float> Time from which the data should be loaded " +
             "(steady state)"
    )
    parser.add_argument(
        "--current-iteration",
        "-i",
        type=int,
        help="<int> Tells this script what parts of the data to operate " +
             "on. " +
             "For parallel processing. Probably not relevant to set by " +
             "hand since python on itself cannot be run in parallel " +
             "and the batch script will set this option automatically " +
             "if parallel processing of the output data was enabled"
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        help="<string> Name of the outfile (default: ./out.txt)"
    )
    parser.add_argument(
        "--experiment-filter",
        "-e",
        type=str,
        help="<string> The experiment the data should get loaded from"
    )
    parser.add_argument(
        "--module-filter",
        "-m",
        type=str,
        help="<string> Filters which modules the results should " +
             "be loaded from"
    )
    parser.add_argument(
        "--quantiles-to-estimate",
        "-q",
        type=str,
        help="<string> quantiles which should be calculated in the form " +
             "'(float,float,float'"
    )
    parser.add_argument(
        "--confidence-level",
        "-c",
        type=float,
        help="<float> Confidence level for the standard confidence interval"
    )
    args = parser.parse_args()

    # If not set then set some values as their default
    if args.batch_size is None:
        args.batch_size = 1024
    if args.current_iteration is None:
        args.current_iteration = 1
    if args.outfile is None:
        args.outfile = "./out.txt"
    if args.steady_state_starting_time is None:
        args.steady_state_starting_time = -math.inf
    if args.indipendent_replications is None:
        print("Error: Number of indipendent replications has to be set " +
              "as an option. Use -i <indipendent replications> or call " +
              "this script with -h to get more info")
        exit(1)
    if args.confidence_level is None:
        args.confidence_level = 0.95
    if args.quantiles_to_estimate is None:
        args.quantiles_to_estimate = "(0.5)"
    args.quantiles_to_estimate = \
        [float(x) for x in args.quantiles_to_estimate.strip("()").split(",")]

    return args
