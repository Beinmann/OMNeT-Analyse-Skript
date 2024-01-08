import glob
import re
import numpy as np
import statistics as stat
import sys

class ResultPresenter():
    quantile_suffix = "Quantile_est"
    standard_ci_suffix = "Standard_ci"
    min_max_ci_suffix = "min_max_ci"
    pull_dir = None
    pull_from_other_temp = None

    def __init__(self):
        self.files = glob.glob("*")
        pattern = r".*_(\d+(\.\d+)?)"
        self.quantile_options = []
        for file_name in self.files:
            match = re.search(pattern, file_name)
            if match:
                number = match.group(1)
                self.quantile_options.append(float(number))
        self.quantile_options = list(set(self.quantile_options))
        self.quantile_options.sort()

        self.quantile_selectors = "123456789bcdefghijklmnopqrstuvwxyz"

        self.true_quantile_values = {}

    def get_matching_files(self, pattern, path=None):
        matching_files = []
        files = None
        if path is None:
            files = self.files
        else:
            files = glob.glob(f"{path}/*")
        for file_name in files:
            match = re.search(pattern, file_name)
            if match:
                matching_files.append(file_name)
        return matching_files

    def show_quantile_info(self, quantile):
        numbers = self.get_quantile_estimation_list_certain_quantile(quantile)
        print(f"Info for Quantile: {quantile}")
        print(f"  num observations: {len(numbers)}")
        print(f"  mean: {np.mean(numbers)}")
        print(f"  variance: {stat.variance(numbers)}")
        print()
        print()

    def get_quantile_estimation_list_certain_quantile(self, quantile, path):
        pattern = f".*_{self.quantile_suffix}_{quantile}"
        quantile_file = self.get_matching_files(pattern, path)[0]
        numbers = []
        with open(quantile_file, "r") as f:
            for line in f:
                numbers.append(float(line))
        return numbers

    def get_quantile_selection_from_user(self):
        input_string = (
            "For which quantiles would you like to see the stats?"
            "\n  'a' to show all, otherwise enter a string of "
            "letters corresponding to the quantiles you want to see info for"
            "\n  (example: input '123' would give info for the first "
            "3 quantiles"
        )
        for i, quantile in enumerate(self.quantile_options):
            input_string += f"\n\t{self.quantile_selectors[i]} - {quantile} quantile"
        input_string += "\n"

        x = input(input_string)
        x = x.strip(" _,;'")

        selected_quantiles = []
        if x == "a":
            selected_quantiles = self.quantile_options
        else:
            for ch in x:
                selected_quantiles.append(
                    self.quantile_options[self.quantile_selectors.find(ch)]
                )
        return selected_quantiles

    def get_quantile_estimation_stats(self):
        selected_quantiles = self.get_quantile_selection_from_user()
        print()
        print()
        print()
        for quantile in selected_quantiles:
            self.show_quantile_info(quantile)

    def show_confidence_interval_info(
        self,
        quantile,
        suffix,
        true_quantile,
        pull_data,
        pull_from_other,
        do_not_estimate_coverage
    ):
        pattern = f".*_{suffix}_{quantile}"
        confidence_interval_file_path = self.get_matching_files(pattern)[0]

        if pull_data:
            true_quantile = np.mean(self.get_quantile_estimation_list_certain_quantile(quantile))
        if pull_from_other:
            if self.pull_from_other_temp:
                x = input("Reuse the last selected folder? (y/n)\n")
                if x == "y" or x == "yes":
                    x = input("Select dir to pull quantile estimates from\n")
                    self.pull_dir = x
                else:
                    self.pull_dir = None
                self.pull_from_other_temp = False
            if self.pull_dir is None:
                x = input("Select pull directory path:\n")
                self.pull_dir = x
            true_quantile = np.mean(self.get_quantile_estimation_list_certain_quantile(quantile, self.pull_dir))
            lower_bounds, upper_bounds = get_confidence_interval_bounds_from_file(confidence_interval_file_path)

        n = len(lower_bounds)
        print(f"Info for {suffix}: {quantile} - {suffix}")
        print(f"  num observations: {n}")

        def contains_true_quantile(confidence_interval_index):
            return (
                lower_bounds[confidence_interval_index] <= true_quantile and
                upper_bounds[confidence_interval_index] >= true_quantile
            )
        percent_containing_true_quantile = (
            len(
                [i for i in range(n) if contains_true_quantile(i)]
            ) / n
        )
        print(f"  coverage when compared to {true_quantile}: {percent_containing_true_quantile}")
        print(f"  average lower bound: {np.mean(lower_bounds)}")
        print(f"  average upper bound: {np.mean(upper_bounds)}")
        print(f"  average length:      {np.mean([upper_bounds[i] - lower_bounds[i] for i in range(n)])}")
        # print(f"  mean: {np.mean()}")
        # print(f"  variance: {stat.variance(numbers)}")
        print()
        print()

    def get_confidence_interval_stats(self):
        x = input("For which type of confidence interval would you like to see the stats?\n  1: min-max confidence interval\n  2: standard confidence interval\n  3: both\n")
        show_standard = False
        show_min_max = False
        if x == "1":
            show_min_max = True
        if x == "2":
            show_standard = True
        if x == "3":
            show_min_max = True
            show_standard = True
        print()
        print()
        selected_quantiles = self.get_quantile_selection_from_user()
        print()
        print()
        print()
        x = input(
            "Would you like to see the confidence intervals coverage?"
            "\nIf so then how would you like to select the true quantile"
            "\nTo compare to?"
            "\n  1: Pull data from this folder"
            "\n  2: Enter each quantile manually"
            "\n  3: Pull data from other folder"
            "\n  4: Don't estimate coverage\n"
        )
        pull_data = False
        enter_manually = False
        estimate_coverage = True
        pull_from_other = False
        if x == "1":
            pull_data = True
        if x == "2":
            enter_manually = True
        if x == "3":
            pull_from_other = True
            if self.pull_dir is not None:
                self.pull_from_other_temp = True
        if x == "3":
            estimate_coverage = False

        for quantile in selected_quantiles:
            true_quantile_to_compare_to = None
            if enter_manually:
                true_quantile_to_compare_to = float(input(f"Enter {quantile}-Quantile to compare to for estimating the coverage"))
            suffix_list = []
            if show_standard:
                suffix_list.append(self.standard_ci_suffix)
            if show_min_max:
                suffix_list.append(self.min_max_ci_suffix)
            for suffix in suffix_list:
                self.show_confidence_interval_info(
                    quantile=quantile,
                    suffix=suffix,
                    true_quantile=true_quantile_to_compare_to,
                    pull_data=pull_data,
                    pull_from_other=pull_from_other,
                    do_not_estimate_coverage=not estimate_coverage
                )

    def write_new_files_with_confidence_interval_analysis(self, path):
        for suffix in [self.standard_ci_suffix, self.min_max_ci_suffix]:
            pattern = f".*_{suffix}_(\\d+(\\.\\d+)?)"
            files = glob.glob("*")

            with open(f"Analysis_result_{suffix}.txt", "w") as newfile:
                newfile.write("quantile,coverage\n")
                quantile_files = glob.glob(f"{path}/*")
                for file_name in files:
                    match = re.match(pattern, file_name)
                    if match:
                        lower_bounds, upper_bounds = get_confidence_interval_bounds_from_file(file_name)
                        quantile = match.group(1)
                        quantile_estimations = self.get_quantile_estimation_list_certain_quantile(quantile, path)
                        overall_quantile_estimation = np.mean(quantile_estimations)
                        num_true_estimates_in_confidence_interval = 0
                        for i in range(len(lower_bounds)):
                            if (lower_bounds[i] <= overall_quantile_estimation and upper_bounds[i] >= overall_quantile_estimation):
                                num_true_estimates_in_confidence_interval = num_true_estimates_in_confidence_interval + 1
                        coverage = num_true_estimates_in_confidence_interval / len(lower_bounds)
                        newfile.write(f"{quantile},{coverage}\n")


# Helper functions
def get_confidence_interval_bounds_from_file(file_path):
    lower_bounds = []
    upper_bounds = []
    with open(file_path, "r") as f:
        for line in f:
            pattern = r"\((-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\)"
            match = re.match(pattern, line)
            if match:
                lower_bounds.append(float(match.group(1)))
                upper_bounds.append(float(match.group(3)))
            else:
                print(f"Error: Could not match the confidence interval files format as (float, float); {suffix}; quantile {quantile}")
                print(f"Specifically: {line}")
                exit(1)
    return (lower_bounds, upper_bounds)


def get_quantile_estimations_from_file(file_path):
    print("Not implemented")
    exit(1)


if __name__ == "__main__":
    if (len(sys.argv) > 1):
        ResultPresenter().write_new_files_with_confidence_interval_analysis(sys.argv[1])
    else:
        while True:
            x = input("Hello, What would you like to do?\n\t1: Get quantile estimates\n\t2: Show confidence interval stats and coverage\n")
            resultPresenter = ResultPresenter()
            if x == "1":
                resultPresenter.get_quantile_estimation_stats()
            elif x == "2":
                resultPresenter.get_confidence_interval_stats()

            print()
            print()
            x = input("Go again with other parameters? (y/n)\n")
            if x == "n" or x == "no":
                break
