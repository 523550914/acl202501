import argparse
from src.template import *
from src.api import *
import json
from tqdm import tqdm

def generate_fuzzy_data(all_query, hybrid_query, model_name):
    # TODO: 实现生成模糊数据的逻辑
    for d in all_query:
        if hybrid_query == d['query']:
            tool_list_str = ''
            for api in d['api_list']:
                api_identity = [api['tool_name'], api['api_name']]
                if api_identity in d['relevant APIs']:
                    tool_list_str += f"[tool_name:{api['tool_name']},api_name:{api['api_name']}],"
            tool_list_str=tool_list_str[:-1]
            print(tool_list_str)
            prompt = fuzzy_template.format(instruction=d['query'], apis=tool_list_str)
            response = generate_data(prompt, model_name)
            print(response)
            print('*'*50)
            return response            


if __name__ == '__main__':
    parser = argparse.ArgumentParser()  
    parser.add_argument('--input_file', type=str, default='/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/hybrid/train.query.txt', help='input file path')
    parser.add_argument('--output_file', type=str, default='/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/fuzzy/train.query.txt', help='output file path')
    parser.add_argument('--model_name', type=str, default='microsoft/DialoGPT-medium', help='model name')
    parser.add_argument('--all_qeury_json',type=str)
    args = parser.parse_args()
    with open(args.all_qeury_json,'r') as f:
        all_query = json.load(f)
    with open(args.input_file,'r') as f:
        orig_data = f.readlines()
    with open(args.output_file,'w') as f:
        for line in tqdm(orig_data):
            split_query = line.split('\t')
            fuzzy_sentence = generate_fuzzy_data(all_query, split_query[1].strip(), args.model_name)
            f.write(f"{split_query[0]}\t{fuzzy_sentence}\n")
        print('finish')