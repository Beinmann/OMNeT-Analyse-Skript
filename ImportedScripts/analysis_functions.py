import numpy as np
import math
from scipy.stats import t
from ImportedScripts.params import Params

# Helper functions for Analysis
def calculate_batch_quantiles(params: Params) -> list[float]:
    """
    Calculate the quantile batches as in forumla (30) from
    Steady State simulation
    """
    vecvalues = (
        [params.df.at[j, params.dataframe_col_name][0:params.min_vecvalue_length]
         for j in range(params.num_replications)]
    )
    vecvalues = np.array(vecvalues, dtype=object)
    reshaped_vecvalues = vecvalues.T.reshape(-1, params.num_replications)

    quantiles = np.quantile(reshaped_vecvalues, params.quantile_to_estimate, axis=1)

    quantiles = np.array(quantiles)
    batch_quantiles = []
    for i in range(params.num_batches):
        starting_index = i * params.batch_size
        end_index = (i + 1) * params.batch_size
        mean = np.mean(quantiles[starting_index:end_index])
        batch_quantiles.append(mean)
    return batch_quantiles


# from "steady state quantile estimation" forumla (31)
def calculate_variance_from_batched_quantiles(
        params: Params,
        batch_quantiles: list[float],
) -> float:
    num_batches = params.num_batches
    overall_quantile_estimation = np.mean(batch_quantiles[0:num_batches])
    factor = 1 / (num_batches * (num_batches - 1))
    sum_of_squared_diff = 0
    for i in range(num_batches):
        sum_of_squared_diff += \
                (batch_quantiles[i] - overall_quantile_estimation)**2
    variance_estimate = factor * sum_of_squared_diff

    return variance_estimate


def calculate_standard_confidence_interval(
        params: Params,
        quantile_estimate: float,
        variance_estimate: float,
):
    """
    Diese Funktion berechnet ein Konfidenzintervall für ein Quantil aus einer
    Steady-State-Simulation

    Es wird die Methode der Batch-Means verwendet, um die Varianz der Daten
    zu Schätzen. Wie in "Steady State Quantile Estimation"
    """

    alpha = 1 - params.confidence_level
    degrees_of_freedom = params.num_batches
    std_dev = math.sqrt(variance_estimate)
    t_quantile = t.ppf(alpha / 2, degrees_of_freedom)

    # the (estimate for the quantile minus the actual Quantile) divided by
    # std_dev is approximately t-distributed with num_batches degrees of freedom
    # Calculate the bounds for the confidence interval
    lower_bound = quantile_estimate + t_quantile * std_dev
    upper_bound = quantile_estimate - t_quantile * std_dev
    return (lower_bound, upper_bound)


def estimate_quantiles_of_whole_steady_state_data_for_all_replications(
    params: Params
):
    n = len(params.df)
    vecvalues = [params.df.at[i, params.dataframe_col_name] for i in range(n)]
    calculated_quantiles = [
        np.quantile(vecvalues[i], params.quantile_to_estimate) for i in range(n)
    ]
    return calculated_quantiles


def calculate_overall_quantile_of_steady_state_distribution(params: Params):
    n = len(params.df)
    vecvalues = [params.df.at[i, params.dataframe_col_name] for i in range(n)]
    all_vecvalues = np.concatenate(vecvalues)
    calculated_overall_quantile = (
        np.quantile(all_vecvalues, params.quantile_to_estimate)
    )
    return calculated_overall_quantile


def is_true_parameter_in_confidence_interval(
        params: Params,
        confidence_interval_lower_bound: float,
        confidence_interval_upper_bound: float
        ) -> bool:
    true_parameter = params.true_parameter
    if (
        true_parameter >= confidence_interval_lower_bound and
        true_parameter <= confidence_interval_upper_bound
    ):
        return True
    else:
        return False
