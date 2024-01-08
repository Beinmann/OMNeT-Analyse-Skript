#!/bin/sh
# example call: ./myBashScript.sh 10 --do-estimate-quantile -q 0.5 -i 1000 -n 5 -p 8 -m -s 123

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo " at least one of the following 4 has to be set" 
    echo "  --calculate-all, -a                       activates the three options below, estimating quantiles and"
    echo "                                            calculating standard and min-max confidence intervals each"
    echo "                                            iteration. These calculations take very little time compared"
    echo "                                            to loading the result files"
    echo "  --do-estimate-quantile                    When this is set, estimate the quantile each iteration and"
    echo "                                            write that to the outfile"
    echo "  --do-calculate-min-max-ci                  Min-max confidence interval will get calculated and written"
    echo "                                            to the outfile"
    echo "  --do-calculate-standard-ci                Calculate the Confidence using the batch means method and"
    echo "                                            write it to the outfile."
    echo "  -h, --help                                Display help"
    echo "  -r, --indipendent-replications <num>      How many indipendent replications of the simulation are run"
    echo "  -i, --iterations <num>                    Run the simulation(s) multiple times, analyzing results each time"
    echo "  -m, --make                                Call opp_make before first simulation run"
    echo "  -c, --clear-past-results                  Clear results directory at script start"
    echo "  -p, --max-parallel-processes <num>        Max parallel simulations (default: 8)"
    echo "  -n, --num-iterations-per-cycle <num>      Iterations run before they are analyzed in parallel"
    echo "                                            (default: 1 - meaning no parallel analysis)"
    echo "                                            Info: If this is set to a value greater than 1"
    echo "                                            it will create n temporary files analysis_result_suffix_n"
    echo "                                            in place before deleting them"
    echo "  -s, --seed <num>                          Set seed (default: random)"
    echo "  --estimated-quantile, -q <num>            What quantile should be estimated (default: 0.5)"
    echo "  --estimate-multiple-quantiles <list>      The analysis is repeated for multiple quantiles."
    echo "                                            This will override the --estimated-quantile setting"
    echo '                                            Inputs in the form of "(0.05,0.3,0.5,0.8)" are accepted'
    echo "  -b, --batch-size <num>                    Batch size for standard method (default: 64)"
    echo "  --confidence-level <num>                  Confidence level only for the standard method (default: 0.95)"
    echo "  --simulation-file, -sim <string>          Simulation file to run (example: ./TicToc)"
    echo "  --omnetpp-ini, --ini                      name of the ini file for the simulation (default: omnetpp.ini)"
    echo "  --config-name, --config <string>          Config name of the omnetpp simulation (from ini file)"
    echo "  --experiment-name, --exp <string>         Experiment name (will be used as a filter for the values)"
    echo "                                            Defaults to the config name"
    echo "  --module-name, --mod <string>             Module name for the results of the omnetpp simulation (will be used as a filter)"
    echo "                                            In case these filters are not enough to filter exactly the values you need"
    echo "                                            further modification of the python script is needed"
    echo "                                            (main.py or ImportedScripts.load_result_files.py)"
    echo "  --extra-info, -extra <string>             Anything that should be appended to the directory name that the results"
    echo "                                            are saved to"
    exit 1
} 

help_text() {
    echo "Help for $0"
    echo "This script runs the simulation with a specified number of indipendent replications and then analyzes the results using python. Below are the arguments which are available. At least one of (estimate quantiles, calculate standard confidence interval or calculate min max confidence interval) has to be set for this script to analyze the results. For this either the flags can be set manually or alternatively -a activates all three. The analysis of the results takes comparatively little time when compared to loading the result files. How often the process of running the simulation and then analyzing the results is repeated is set with the iterations option. This script will run the simulations in parallel unless -p is set to 1. The python analysis can also be run in parallel if -n is greater than 1 and -p is set to a value bigger than 1. However when -n is set to a value greater than one that also means that the results of multiple iterations have to be saved on the disc at once so be aware of that when using -n > 1 for large simulations."
    echo ""
    usage
    exit 1
}

# Check if help or usage has to be shown
if [ "$#" -lt 1 ]; then
    usage
fi

# Set defauls for most values
num_indipendent_replications=1
do_make=false
clear_past_results=false
iterations=1
max_parallel_processes=8
num_iterations_per_cycle=1
outfile="./AnalysisScriptResults/out.txt"
standard_ci_suffix="standard_ci"
min_max_ci_suffix="min-max_ci"
quantile_estimation_suffix="quantile"
do_quantile_estimation=false
do_standard_ci=false
do_min_max_ci=false
# Seed offset (applies to all runs, will get incremented by one for each simulation).
# Needs to be exported so it can be used in the run_simulation function
seed_offset=$RANDOM
quantiles_to_estimate="(0.5)"
batch_size=64
confidence_level=0.95
simulation=./BankTeller
config="BankTeller"
experiment_name=$config
module_name=BankTeller.queue
omnetpp_ini_name="omnetpp.ini"

# Read commandline arguments and set values depending on the inputs
while test $# -gt 0; do
    case "$1" in
        -h|--help)
            help_text
            break
            ;;
        -i|--iterations)
            iterations=$2
            shift
            ;;
        -m|--make)
            do_make=true
            ;;
        -r|--indipendent-replications)
            num_indipendent_replications=$2
            shift
            ;;
        -c|--clear-past-results)
            clear_past_results=true
            ;;
        -p|--max-parallel-processes)
            max_parallel_processes=$2
            shift
            if [ $max_parallel_processes -lt 1 ]; then
                echo "Error: --max-parallel-processes set to a number less than 1"
                exit 1
            fi
            ;;
        -n|--num-iterations-per-cycle)
            num_iterations_per_cycle=$2
            shift
            ;;
        -q|--estimated_quantile)
            quantiles_to_estimate="($2)"
            shift
            ;;
        --estimate-multiple-quantiles)
            quantiles_to_estimate=$2
            shift
            ;;
        --s|--seed)
            if [ "$2" != "random" ]; then
                seed_offset=$2
            fi
            shift
            ;;
        --calculate-all|-a)
            do_quantile_estimation=true
            do_min_max_ci=true
            do_standard_ci=true
            ;;
        --do-estimate-quantile)
            do_quantile_estimation=true
            ;;
        --do-calculate-min-max-ci)
            do_min_max_ci=true
            ;;
        --do-calculate-standard-ci)
            do_standard_ci=true
            ;;
        -b|--batch-size)
            batch_size=$2
            shift
            ;;
        --confidence-level)
            confidence_level=$2
            shift
            ;;
        --sim|--simulation-file)
            simulation=$2
            shift
            ;;
        --omnetpp-ini|--ini)
            omnetpp_ini_name=$2
            shift
            ;;
        --config-name|--config)
            config=$2
            shift
            ;;
        --experiment-name|--exp)
            experiment_name=$2
            shift
            ;;
        --module-name|--mod)
            module_name=$2
            shift
            ;;
        --extra-info|--extra)
            extra_info=$2
            shift
            ;;
        *)
            echo "Invalid argument: $1"
            echo "Call this Script with -h to see usage"
            exit 1
            ;;
    esac
    if test $# -lt 1; then
        echo "Error: used an option that takes a parameter but then provided none"
        echo ""
        usage
    fi
    shift
done

# Random things that can be changed but don't need to
quantile_estimation_suffix="Quantile_est"
standard_ci_suffix="Standard_ci"
min_max_ci_suffix="min_max_ci"
sleeping_time_between_iterations=0


# Go up one directory from Analysis Script so all the commands
# Below run from the main directory of the Omnetpp Project
cd ..

# Determine the output file names
dir_path=$(dirname "$outfile")
extension="${outfile##*.}"
file_name=$(basename "$outfile" .$extension)
cur_date=$(date +'%Y.%m.%d_%H-%M')

if [ "$extension" != "txt" ]; then
    echo "Error: currently only .txt file ending for the outfile supported"
    exit 1
fi

dir_path="${dir_path}/${cur_date}_${config}_Simulation_${extra_info}"
if [ ! -d "$dir_path" ]; then
    mkdir -p "$dir_path"
fi

info_outfile="${dir_path}/run_parameters_and_info.${extension}"
outfile="${dir_path}/${file_name}.${extension}"
echo "" >> $info_outfile
echo "$cur_date, Starting Simulation with parameters" >> $info_outfile
printf "    %-8s %s\n" "$num_indipendent_replications," " Indipendent Replications per Iteration" >> $info_outfile
printf "    %-8s %s\n" "$iterations," " Iterations (Script might have been stopped before)" >> $info_outfile
printf "    %-8s %s\n" "$quantiles_to_estimate," "Estimated quantile(s)" >> $info_outfile
printf "    %-8s %s\n" "$seed_offset," " Seed" >> $info_outfile
printf "    %-8s %s\n" "$do_make," " Do Make" >> $info_outfile
printf "    %-8s %s\n" "$clear_past_results," " Cleared results dir before first simulation run" >> $info_outfile
printf "    %-8s %s\n" "$max_parallel_processes," " Max parallel processes (Global)" >> $info_outfile
printf "    %-8s %s\n" "$num_iterations_per_cycle," " Max parallel python analysis scripts" >> $info_outfile
echo "" >> $info_outfile

# Remove leading "./" if present from omnetpp_ini_name and then copy the ini to the current run directory
omnetpp_ini_name="${omnetpp_ini_name#./}"
cp "./${omnetpp_ini_name}" "${dir_path}/${omnetpp_ini_name}_backup"

if $do_make; then
    make
    echo ""
fi

if $clear_past_results; then
    echo "Clearing results dir"
    echo ""
    DIR="./results"
    # Check if the directory exists
    if [ -d "$DIR" ]; then
        # Remove the directory and its contents
        rm -r "$DIR"
        echo "Results directory deleted."
    else
        echo "Results directory does not exists. Proceeding as usual"
    fi
fi

# how often times the script will actually get run
true_iterations=$((iterations / num_iterations_per_cycle))

last_time=$(date +%s%3N)
for ((i=0; i<iterations; i=i+num_iterations_per_cycle)) do

    completed_iterations=$i
    remaining_iterations=$((iterations - completed_iterations))

    # Iterations this current cycle of the for loop is either "num_iterations_per_cycle" if there are at least that
    # many remaining iterations. Otherwise the iterations this cycle are the remaining ones
    if [ $remaining_iterations -lt $num_iterations_per_cycle ]; then
        iterations_this_cycle=$remaining_iterations
    else
        iterations_this_cycle=$num_iterations_per_cycle
    fi

    if [ $num_iterations_per_cycle -eq 1 ]; then
        echo "Iteration $((i + 1)) of $iterations"
    else
        echo "Iterations $((completed_iterations + 1))..$((completed_iterations + iterations_this_cycle)) of $iterations"
    fi

    # Export most variables so they can be used in the scripts running in the background
    export simulation
    export num_indipendent_replications
    export i
    export config
    export experiment_name
    export module_name
    export outfile
    export confidence_level
    export quantiles_to_estimate
    export quantile_estimation_suffix
    export standard_ci_suffix
    export min_max_ci_suffix
    export do_min_max_ci
    export do_quantile_estimation
    export do_standard_ci
    export batch_size
    export confidence_level
    export seed_offset

    run_simulation() {
        runnr=$(($1-1))
        seed=$(($runnr + (num_indipendent_replications * i) + seed_offset))
        sleep $(($runnr * sleeping_time_between_iterations))
        $simulation -s -u Cmdenv -c $config -r $runnr --seed-set=$seed --cmdenv-redirect-output=true
    }
    export -f run_simulation

    # Run the simulation
    times_run_this_cycle=$((num_indipendent_replications * iterations_this_cycle))
    seq $times_run_this_cycle | xargs -I{} -P $max_parallel_processes -n 1 bash -c 'run_simulation {}'
    echo ""
    echo "Done, starting analysis with Python"
    echo ""


    run_analysis() {
        runnr=$(($1-1))
        mode_string=""
        if [ "$do_quantile_estimation" = true ]; then
            mode_string="${mode_string}--do-estimate-quantile $quantile_estimation_suffix "
        fi
        if [ "$do_standard_ci" = true ]; then
            mode_string="${mode_string}--do-calculate-standard-confidence-interval $standard_ci_suffix "
        fi
        if [ "$do_min_max_ci" = true ]; then
            mode_string="${mode_string}--do-calculate-min-max-confidence-interval $min_max_ci_suffix "
        fi
        python AnalysisScript/main.py \
            -r $num_indipendent_replications \
            -i $runnr \
            -b $batch_size \
            $mode_string\
            -m $module_name \
            -e $experiment_name \
            -o "$outfile" \
            -q "$quantiles_to_estimate" \
            -c $confidence_level
        
    }
    export -f run_analysis
    seq $iterations_this_cycle | xargs -I{} -P $max_parallel_processes -n 1 bash -c 'run_analysis {}'
    python AnalysisScript/post_analysis_script_cleanup.py $dir_path

    end=$(date +%s%3N)
    difference=$((end - last_time))
    last_time=$end
    echo "Iterations $((i+1)) until $((i + num_iterations_per_cycle)) finished; Time taken: $difference milliseconds; With $num_indipendent_replications indipendent replications each iteration this amounts to $(( (i + num_iterations_per_cycle) * num_indipendent_replications)) single runs simulated" >> $info_outfile
    echo "Time taken: $difference milliseconds"
    echo ""
    echo ""

done
