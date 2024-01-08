import math
from omnetpp.scave import results


def get_vectors_from_result_files(
        start_replication,
        end_replication,
        experiment_name,
        module_name,
        start_time=None,
        end_time=None):
    if start_time is None:
        start_time = - math.inf
    if end_time is None:
        end_time = math.inf
    type_filter = 'type =~ vector'
    experiment_filter = f'runattr:experiment =~ {experiment_name}'
    replication_filter = (
        f'runattr:replication =~ "#{{{start_replication}..{end_replication}}}"'
    )
    module_filter = f'module =~ {module_name}'
    name_filter = 'name =~ customerWaitingTime:vector'

    filter_expression = f'{type_filter} AND {experiment_filter} AND {replication_filter} AND {module_filter} AND {name_filter}'

    full_df = results.read_result_files(
            filenames=["./results/BankTeller*.vec", "./results/BankTeller*.sca"],
            filter_expression=filter_expression,
            include_fields_as_scalars=False,
            vector_start_time=start_time,
            vector_end_time=end_time
    )
    if (len(full_df) == 0):
        # TODO raise  a more fitting exception
        raise Exception("No files found or no data contained in the analyzed files after applying the filter expression")

    # TODO handle the potential results.ResultQueryError
    df = results.get_vectors(full_df, include_attrs=True, include_runattrs=True, include_itervars=True, start_time=start_time, end_time=end_time)
    if (len(df) == 0):
        # TODO raise  a more fitting exception
        raise Exception("Filtered dataframe empty")

    return df
