from ImportedScripts.analysis_functions import estimate_quantiles_of_whole_steady_state_data_for_all_replications, calculate_variance_from_batched_quantiles, calculate_standard_confidence_interval, calculate_overall_quantile_of_steady_state_distribution, is_true_parameter_in_confidence_interval, calculate_batch_quantiles
from ImportedScripts.params import Params
import numpy as np
import pandas as pd
import os


def calculate_standard_confidence_interval_from_df(params: Params):
    """
    Take the results dataframe as input and go through all steps to calculate
    a confidence interval using the standard method of estimating the variance
    using batch means and then calculating the confidence interval using
    this variance
    """
    batch_quantiles = calculate_batch_quantiles(params)
    # num_batches = len(batch_quantiles)
    estimated_batch_variance = calculate_variance_from_batched_quantiles(
        params,
        batch_quantiles
    )
    standard_confidence_interval = calculate_standard_confidence_interval(
        params=params,
        quantile_estimate=(
            calculate_overall_quantile_of_steady_state_distribution(params)
        ),
        variance_estimate=estimated_batch_variance,
    )

    write_confidence_interval_and_info_into_outfile(
        params=params,
        ci=standard_confidence_interval,
        confidence_interval_name=params.standard_ci_suffix
    )


def calculate_min_max_confidence_interval(params: Params):
    quantile_estimates = (
        estimate_quantiles_of_whole_steady_state_data_for_all_replications(
            params
        )
    )
    ci = (min(quantile_estimates), max(quantile_estimates))
    return ci


def calculate_quantile_and_write_to_file(
    params: Params
):
    """
    Calculates the quantile estimate and appends it to the outfile
    """
    calculated_quantile = \
        calculate_overall_quantile_of_steady_state_distribution(params)
    write_to_outfile(
        params=params,
        string_to_write=str(calculated_quantile),
        file_suffix=params.quantile_suffix
    )


def write_confidence_interval_and_info_into_outfile(
    params: Params,
    ci: tuple[float, float],
    confidence_interval_name: str = None
):
    write_to_outfile(
        params=params,
        string_to_write=f"{ci}",
        file_suffix=confidence_interval_name
    )


def write_to_outfile(
    params: Params,
    string_to_write: str,
    file_suffix: str = None
):
    if file_suffix is None:
        file_suffix = ""
    else:
        file_suffix = f"{file_suffix}_"
    base, extension = os.path.splitext(params.outfile_path)
    outfile_with_suffix = (
        f"{base}_{file_suffix}"
        f"{params.quantile_to_estimate}_"
        f"{params.current_iteration}{extension}"
    )
    with open(outfile_with_suffix, "a+") as f:
        f.write(string_to_write + "\n")
