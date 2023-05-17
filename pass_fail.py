###################################################################################################
#
# Copyright (C) 2020 Maxim Integrated Products, Inc. All Rights Reserved.
#
# Maxim Integrated Products, Inc. Default Copyright Notice:
# https://www.maximintegrated.com/en/aboutus/legal/copyrights.html
#
###################################################################################################
"""
Check the test results
"""
import argparse
import os
import yaml

from log_comparison import not_found_model, map_value_list


parser = argparse.ArgumentParser()
parser.add_argument('--testconf', help='Enter the config file for the test', required=True)
args = parser.parse_args()
yaml_path = args.testconf

# Open the YAML file
with open(yaml_path, 'r') as file:
    # Load the YAML content into a Python dictionary
    config = yaml.safe_load(file)

log_path = r'/home/asyaturhal/desktop/ai/log_diff'
# log_path = r'C:\Users\aturhal\Desktop\test_logs'
log_path = log_path + '/' + sorted(os.listdir(log_path))[-1]


def check_top_value(file, threshold, map_value):
    """
    Compare Top1 value with threshold
    """
    if not map_value:
        with open(file, 'r', encoding='utf-8') as f:

            model_name = file.split('/')[-1].split('___')[0]
            # Read all lines in the file
            lines = f.readlines()
            # Extract the last line and convert it to a float
            top1 = lines[-1].split()
            epoch_num = int(top1[0])
            top1_diff = float(top1[1])
            # top5_diff = float(top1[2])

        if top1_diff < threshold:
            print(f"\033[31m\u2718\033[0m Test failed for {model_name} since"
                  f" Top1 value changed {top1_diff} % at {epoch_num}th epoch.")
            return False
        print(f"\033[32m\u2714\033[0m Test passed for {model_name} since"
              f" Top1 value changed {top1_diff} % at {epoch_num}th epoch.")
        return True
    if map_value:
        with open(file, 'r', encoding='utf-8') as f:

            model_name = file.split('/')[-1].split('___')[0]
            # Read all lines in the file
            lines = f.readlines()
            # Extract the last line and convert it to a float
            top1 = lines[-1].split()
            epoch_num = int(top1[0])
            top1_diff = float(top1[1])
            # top5_diff = float(top1[2])

        if top1_diff < threshold:
            print(f"\033[31m\u2718\033[0m Test failed for {model_name} since"
                  f" mAP value changed {top1_diff} % at {epoch_num}th epoch.")
            return False
        print(f"\033[32m\u2714\033[0m Test passed for {model_name} since"
              f" mAP value changed {top1_diff} % at {epoch_num}th epoch.")
        return True


passing = []

for item in not_found_model:
    print("\033[93m\u26A0\033[0m " + "Warning: " + item)

for logs in sorted(os.listdir(log_path)):
    log_name = (logs.split("___"))[0]
    log_model = log_name.split("-")[0]
    log_data = log_name.split("-")[1]

    if log_data in config and log_model in config[log_data]:
        threshold_temp = float(config[f'{log_data}'][f'{log_model}']['threshold'])
    else:
        threshold_temp = 0
    logs = log_path + '/' + str(logs)
    passing.append(check_top_value(logs, threshold_temp, map))

if not all(passing):
    print("\033[31mAll tests did not passed. Cancelling github actions.")
    exit(1)
