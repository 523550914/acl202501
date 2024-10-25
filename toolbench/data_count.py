
import json
with open('/dat03/zly/ToolPlanner/data/toolbench/test_data/G3/hybrid/toolbench_toolllama.json','r') as test_f:
    test_data = json.load(test_f)
    print(len(test_data))
with open('/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/state/train.query.txt','r') as re_train_f:
    re_train_data = re_train_f.readlines()
    print(len(re_train_data))
with open('/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/state/test.query.txt','r') as re_test_f:
    re_test_data = re_test_f.readlines()
    print(len(re_test_data))

with open('/dat03/zly/ToolPlanner/data/toolbench/instruction/G3_query.json','r') as ins_f:
    ins_data = json.load(ins_f)
    print(len(ins_data))


import os

# Set the directory path
directory_path = '/dat03/zly/ToolPlanner/data/toolbench/answer/G3_answer'

# Get the list of all files in the directory
try:
    files = os.listdir(directory_path)
    file_count = len(files)
    print(f'Total number of files: {file_count}')
except FileNotFoundError:
    print('Directory not found')
