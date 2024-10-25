import json
import os

from prompt import *

def process_data(state_input_file, hybrid_output_file, sft_file):
    with open(state_input_file, "r") as state_f, open(hybrid_output_file, "r") as hybrid_f:
        train_data_list = []
        hybrid_querys = hybrid_f.readlines()
        for i, query in enumerate(state_f.readlines()):
            train_data = {}
            # 提取序号和句子
            state_query = query.split("\t")
            hybrid_query = hybrid_querys[i].split("\t")
            # 写入文件
            train_data['instruction'] = system_prompt.format(request=state_query[1].strip())
            train_data['output'] = hybrid_query[1].strip()
            assert state_query[0] == hybrid_query[0]
            train_data['id'] = state_query[0].strip()
            train_data_list.append(train_data)

    with open(sft_file, "w") as f:
        json.dump(train_data_list, f, ensure_ascii=False, indent=4)

# 文件路径
train_input_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/state/train.query.txt'
train_output_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/hybrid/train.query.txt'
train_sft_file = '/dat03/zly/ToolPlanner/zly_data/first_sentence_model/G3/state2hybrid/sft_train.json'

test_input_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/state/test.query.txt'
test_output_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/hybrid/test.query.txt'
test_sft_file = '/dat03/zly/ToolPlanner/zly_data/first_sentence_model/G3/state2hybrid/sft_test.json'

# 处理train和test数据
process_data(train_input_file, train_output_file, train_sft_file)
process_data(test_input_file, test_output_file, test_sft_file)
