###################################################################################################
#
# Copyright (C) 2020-2022 Maxim Integrated Products, Inc. All Rights Reserved.
#
# Maxim Integrated Products, Inc. Default Copyright Notice:
# https://www.maximintegrated.com/en/aboutus/legal/copyrights.html
#
###################################################################################################
"""
Compare log files of the pulled code and the last developed
"""
import datetime
import os
import sys

import yaml

from tabulate import tabulate


def compare_logs(old_log, new_log, output_name, output_pth):
    """
    Take diff top1 of log files of the pulled code and the last developed
    """
    header = ["Epoch number", "Top1 Diff(%)", "Top5 Diff(%)"]
    header_map = ["Epoch number", "mAP Diff(%)"]

    word = 'Best'
    word2 = 'Top1'
    word3 = 'mAP'
    ex_list = [False]

    with open(new_log, 'r', encoding='utf-8') as f2:
        file2 = f2.read()
        log_name = new_log.split('/')[-1].split('___')[0]

        if word2 not in file2 and word3 not in file2:
            print(f"\033[31m\u2718\033[0m {log_name} does not have any trained results."
                  " There is an error in training.")
            ex_list.append(True)

    if all(ex_list):
        print("\033[31m Cancelling github actions.")
        sys.exit(1)

    with open(old_log, 'r', encoding='utf-8') as f1, open(new_log, 'r', encoding='utf-8') as f2:
        file1_content = f1.readlines()
        file2_content = f2.readlines()

        log1_list = []
        log2_list = []
        mAP_list1 = []
        mAP_list2 = []

        word = 'Best'
        word2 = 'Top1'
        word3 = 'mAP'
        map_value = False

        for line in file1_content:
            if word in line and word2 in line:
                lst = line.split()
                log1_list.append(lst[5:])
                map_value = False
            elif word in line and word3 in line:
                lst = line.split()
                mAP_list1.append(lst[5:7])
                map_value = True

        for line in file2_content:
            if word in line and word2 in line:
                lst = line.split()
                log2_list.append(lst[5:])
                map_value = False
            elif word in line and word3 in line:
                lst = line.split()
                mAP_list2.append(lst[5:7])
                map_value = True

        epoch_num_top = min(len(log1_list), len(log2_list))
        epoch_num_map = min(len(mAP_list1), len(mAP_list2))

        log1_list = log1_list[:epoch_num_top]
        log2_list = log2_list[:epoch_num_top]
        mAP_list1 = mAP_list1[:epoch_num_map]
        mAP_list2 = mAP_list2[:epoch_num_map]

        top1 = []
        map_list = []

    if not map_value:
        i = 0
        for (list1, list2) in zip(log1_list, log2_list):
            i = i+1
            if '[Top1:' in list2:
                top1_diff = ((float(list2[1])-float(list1[1]))/float(list1[1]))*100
                top1.append([i])
                top1[i-1].append(top1_diff)

            if 'Top5:' in list2:
                top5_diff = ((float(list2[3])-float(list1[3]))/float(list1[1]))*100
                top1[i-1].append(top5_diff)

        output_path_2 = output_pth + '/' + output_name + '.txt'
        with open(output_path_2, "w", encoding='utf-8') as output_file:
            output_file.write(tabulate(top1, headers=header))

    if map_value:
        i = 0
        for (map1, map2) in zip(mAP_list1, mAP_list2):
            i = i+1
            if '[mAP:' in map2:
                map_diff = ((float(map2[1])-float(map1[1]))/float(map1[1]))*100
                map_list.append([i])
                map_list[i-1].append(map_diff)

        output_path_2 = output_pth + '/' + output_name + '.txt'
        with open(output_path_2, "w", encoding='utf-8') as output_file:
            output_file.write(tabulate(map_list, headers=header_map))
    return map_value


def log_path_list(path):
    """
    Create log names
    """
    lst = []
    for file in sorted(os.listdir(path)):
        lst.append(file.split("___")[0])
    return lst


log_new = r'/home/asyaturhal/desktop/ai/test_logs/'
log_old = r'/home/asyaturhal/desktop/ai/last_developed/dev_logs/'
# script_path = r"/home/asyaturhal/desktop/ai/test_scripts/output_file.sh"
script_path = r'/home/asyaturhal/actions-runner/_work/ai8x-training/ai8x-training/scripts/output_file.sh'

time = str(datetime.datetime.now())
time = time.replace(' ', '.')
time = time.replace(':', '.')
output_path = r"/home/asyaturhal/desktop/ai/log_diff/" + '/' + str(time)

os.mkdir(output_path)

loglist = sorted(os.listdir(log_new))
loglist_old = sorted(os.listdir(log_old))
old_logs_path = log_old + loglist_old[-1]
new_logs_path = log_new + loglist[-1]

new_log_list = log_path_list(new_logs_path)
old_log_list = log_path_list(old_logs_path)

with open(script_path, 'r', encoding='utf-8') as f:
    scripts_t = f.read()
    scripts = scripts_t.split(' ')
name_indices = [i+1 for i, x in enumerate(scripts) if x == "--name"]
values = [scripts[j] for j in name_indices]

ex_list2 = [False]
for log in values:
    if log not in new_log_list:
        print(f"\033[31m\u2718\033[0m {log} does not have any trained log file."
              " There is an error in training.")
        ex_list2.append(True)

if all(ex_list2):
    print("\033[31m Cancelling github actions.")
    sys.exit(1)

not_found_model = []
map_value_list = {}

for files_new in sorted(os.listdir(new_logs_path)):
    files_new_temp = files_new.split("___")[0]
    if files_new_temp not in old_log_list:
        not_found_model.append(files_new_temp + " not found in last developed log files.")
    for files_old in sorted(os.listdir(old_logs_path)):
        files_old_temp = files_old.split("___")[0]
        if files_old_temp == files_new_temp:

            old_path = old_logs_path + '/' + files_old
            new_path = new_logs_path + '/' + files_new

            old_files = sorted(os.listdir(old_path))
            new_files = sorted(os.listdir(new_path))

            old_log_file = [file for file in old_files if file.endswith(".log")][0]
            new_log_file = [file for file in new_files if file.endswith(".log")][0]

            old_path_log = old_path + '/' + old_log_file
            new_path_log = new_path + '/' + new_log_file

            map_value_list[files_new_temp] = compare_logs(
                old_path_log, new_path_log, files_new, output_path
            )
            break
