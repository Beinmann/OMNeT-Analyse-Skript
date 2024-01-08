if __name__ == "__main__":
    import os
    import glob
    import re
    import sys
    dir_path = sys.argv[1]

    # Combine files that were generated by the concurrently running python scripts
    # into one
    def combine_files(directory):
        os.chdir(directory)

        file_pattern = re.compile(r'(.+)_\d+\.txt$')
        files_to_combine = {}

        for filename in glob.glob('*.txt'):
            match = file_pattern.match(filename)
            if match:
                base_name = match.group(1) + '.txt'
                if base_name not in files_to_combine:
                    files_to_combine[base_name] = []
                files_to_combine[base_name].append(filename)

        for base_name, files in files_to_combine.items():
            with open(base_name, 'a') as main_file:
                for file_name in files:
                    with open(file_name) as sub_file:
                        main_file.write(sub_file.read())
                    os.remove(file_name)

    combine_files(dir_path)
