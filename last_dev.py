###################################################################################################
#
# Copyright (C) 2020-2022 Maxim Integrated Products, Inc. All Rights Reserved.
#
# Maxim Integrated Products, Inc. Default Copyright Notice:
# https://www.maximintegrated.com/en/aboutus/legal/copyrights.html
#
###################################################################################################
"""
Create the last developed code logs for base testing source
"""
import datetime
import git
import os
import subprocess


def joining(lst):
    """
      Join based on the ' ' delimiter
    """
    join_str = ' '.join(lst)
    return join_str

# parser = argparse.ArgumentParser()
# parser.add_argument('--testconf', help='Enter the config file for the test', required=True)
# args = parser.parse_args()
# yaml_path = args.testconf

# # Open the YAML file
# with open(yaml_path, 'r') as file:
#     # Load the YAML content into a Python dictionary
#     config = yaml.safe_load(file)

# Folder containing the files to be concatenated
# script_path = r"/home/asyaturhal/desktop/ai/last_developed/ai8x-training/scripts_test"
script_path = r"/home/asyaturhal/desktop/ai/last_developed/last_dev_source/scripts"

# Output file name and path
output_file_path = r"/home/asyaturhal/desktop/ai/last_developed/dev_scripts/last_dev_train.sh"

# global log_file_names
log_file_names = []


def dev_scripts(script_pth, output_file_pth):
    """
    Create training scripts for the last developed code
    """                                  
    with open(output_file_path, "w", encoding='utf-8') as output_file:
        for filename in os.listdir(script_path):
            # Check if the file is a text file
            if filename.startswith("train"):
                # Open the file and read its contents
                with open(os.path.join(script_path, filename), encoding='utf-8') as input_file:
                    contents = input_file.read()

                    temp = contents.split()
                    temp.insert(1, "\n")
                    i = temp.index('--epochs')
                    j = temp.index('--model')
                    k = temp.index('--dataset')

                    log_model = temp[j+1]
                    log_data = temp[k+1]

                    log_name = temp[j+1] + '-' + temp[k+1]
                    log_file_names.append(filename[:-3])

                    if log_data == "FaceID":
                        continue

                    temp[i+1] = "15"

                    if '--deterministic' not in temp:
                        temp.insert(-2, '--deterministic')

                    temp.insert(-1, '--name ' + log_name)

                    data_name = temp[k+1]

                    # temp.insert(-1, '--data ' + path_data)

                    temp.append("\n")
                    contents = joining(temp)
                    # Replace the number in the "--epochs" script

                    # Write the contents to the output file
                    output_file.write(contents)


def dev_checkout():
    """
    Checkout the last developed code
    """
    repo_url = "https://github.com/MaximIntegratedAI/ai8x-training.git"
    local_path = r'/home/asyaturhal/desktop/ai/last_developed/last_dev_source/'

    try:
        repo = git.Repo(local_path)
    except git.exc.InvalidGitRepositoryError:
        repo = git.Repo.clone_from(repo_url, local_path, branch="develop", recursive=True)

    commit_hash = repo.heads.develop.object.hexsha
    commit_num_path = r"/home/asyaturhal/desktop/ai/last_developed/commit_number.txt"

    try:
        with open(commit_num_path, "r", encoding='utf-8') as file:
            saved_commit_hash = file.read().strip()
    except FileNotFoundError:
        saved_commit_hash = ""

    if commit_hash != saved_commit_hash:
        with open(commit_num_path, "w", encoding='utf-8') as file:
            file.write(commit_hash)
            repo.remotes.origin.pull("develop")

            dev_scripts(script_path, output_file_path)
            cmd_command = (
                "bash /home/asyaturhal/desktop/ai/"
                "last_developed/dev_scripts/last_dev_train.sh"
            )
            subprocess.run(cmd_command, shell=True, check=True)
            source_path = "/home/asyaturhal/actions-runner/_work/ai8x-training/ai8x-training/logs/"
            destination_path = (
                "/home/asyaturhal/desktop/ai/last_developed/dev_logs/"
                + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            )
            subprocess.run(['mv', source_path, destination_path], check=True)


dev_checkout() 
