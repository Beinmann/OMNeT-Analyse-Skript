class Params:
    # TODO read these from the main script arguments
    dataframe_col_name = "vecvalue"

    def __init__(self):
        self.do_calculate_standard_confidence_interval: bool = None
        self.do_calculate_quantile_and_write_to_file: bool = None
        self.do_calculate_min_max_confidence_interval: bool = None
        self.quantile_to_estimate: float = None
        self.batch_size: int = None
        self.current_iteration: int = None
        self.outfile_path: str = None
        self.num_replications: int = None
        self.true_parameter: float = None
        self.num_batches: int = None
        self.confidence_level = None
        self.quantile_suffix = None
        self.standard_ci_suffix = None
        self.min_max_suffix = None
        self.min_vecvalue_length = None
