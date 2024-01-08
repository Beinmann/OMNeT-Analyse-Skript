from ImportedScripts.combined_functions import write_confidence_interval_and_info_into_outfile, calculate_quantile_and_write_to_file, calculate_standard_confidence_interval_from_df, calculate_min_max_confidence_interval
from ImportedScripts.load_result_files import get_vectors_from_result_files
from ImportedScripts.params import Params
import ImportedScripts.parser as parser
import time

if __name__ == "__main__":
    # Parse the input arguments and then add them to the param object
    args = parser.parse_args()

    params = Params()
    params.do_calculate_standard_confidence_interval = \
        args.do_calculate_standard_confidence_interval
    params.do_calculate_quantile_and_write_to_file = args.do_estimate_quantile
    params.do_calculate_min_max_confidence_interval = \
        args.do_calculate_min_max_confidence_interval
    params.batch_size = args.batch_size
    params.current_iteration = args.current_iteration
    params.outfile_path = args.outfile
    params.num_replications = args.indipendent_replications
    params.confidence_level = args.confidence_level
    params.standard_ci_suffix = args.do_calculate_standard_confidence_interval
    params.min_max_suffix = args.do_calculate_min_max_confidence_interval
    params.quantile_suffix = args.do_estimate_quantile
    # args.quantiles_to_estimate is a list of floats in the form of a string
    # It can also be just one "(float)"
    quantiles_to_estimate = \
        args.quantiles_to_estimate

    start_time = args.steady_state_starting_time
    experiment_filter = args.experiment_filter
    module_filter = args.module_filter

    if (
        not params.do_calculate_min_max_confidence_interval and
        not params.do_calculate_quantile_and_write_to_file and
        not params.do_calculate_standard_confidence_interval
    ):
        print("Error: no option set to calculate something, exiting")
        exit(1)

    # Analyze the resultfiles
    # Get results as "df"
    start_replication = params.current_iteration * params.num_replications
    end_replication = start_replication + params.num_replications - 1
    timer_start_time = time.time()
    params.df = get_vectors_from_result_files(
            start_replication,
            end_replication,
            experiment_name=experiment_filter,
            module_name=module_filter,
            start_time=start_time
    )
    timer_end_time = time.time()
    print(f"Time it took to load the results: {timer_end_time - timer_start_time} seconds")
    vecvalues = [
        params.df.at[i, params.dataframe_col_name]
        for i in range(len(params.df))
    ]
    min_vecvalue_length = min([len(x) for x in vecvalues])
    params.min_vecvalue_length = min_vecvalue_length
    params.num_batches = min_vecvalue_length // params.batch_size

    # For each quantile to estimate call the analysis functions
    for quantile_to_estimate in quantiles_to_estimate:
        # TODO delete this outer loop
        # for batch_size in [96]: #[16, 8, 100, 300, 1000, 2, 4]:
        # params.batch_size = batch_size
        params.quantile_to_estimate = quantile_to_estimate

        # Analyze the results. Does different (or multiple) things depending
        #  on which flags were set from the commandline
        if params.do_calculate_standard_confidence_interval:
            calculate_standard_confidence_interval_from_df(params)

        if params.do_calculate_min_max_confidence_interval:
            min_max_ci = calculate_min_max_confidence_interval(params)
            write_confidence_interval_and_info_into_outfile(
                params=params,
                ci=min_max_ci,
                confidence_interval_name=params.min_max_suffix
            )

        if params.do_calculate_quantile_and_write_to_file:
            calculate_quantile_and_write_to_file(params=params)
