import json
import os
from utils.retriever import ToolRetriever
from utils.toolbench_utils import *
import argparse
from tqdm import tqdm

# 检查候选工具是否包含在白名单中
def contain(candidate_list, white_list):
    output = []
    for cand in candidate_list:
        if cand not in white_list.keys():
            return False
        output.append(white_list[cand])
    return output

def api_json_to_openai_json(api_json, standard_tool_name):
    description_max_length = 256
    template = {
        "name": "",
        "description": "",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
            "optional": [],
        }
    }
    
    map_type = {
        "NUMBER": "integer",
        "STRING": "string",
        "BOOLEAN": "boolean"
    }

    pure_api_name = change_name(standardize(api_json["api_name"]))
    template["name"] = pure_api_name + f"_for_{standard_tool_name}"
    template["name"] = template["name"][-64:]

    template["description"] = f"This is the subfunction for tool \"{standard_tool_name}\", you can use this tool."
    
    if api_json["api_description"].strip() != "":
        truncated_description = api_json['api_description'].strip().replace(api_json['api_name'], template['name'])[:description_max_length]
        template["description"] = template["description"] + f"The description of this function is: \"{truncated_description}\""
    
    if "required_parameters" in api_json.keys() and len(api_json["required_parameters"]) > 0:
        for para in api_json["required_parameters"]:
            name = standardize(para["name"])
            name = change_name(name)
            param_type = map_type.get(para["type"], "string")
            prompt = {
                "type": param_type,
                "description": para["description"][:description_max_length],
            }

            default_value = para['default']
            if len(str(default_value)) != 0:    
                prompt["example_value"] = default_value

            template["parameters"]["properties"][name] = prompt
            template["parameters"]["required"].append(name)
        
    for para in api_json["optional_parameters"]:
        name = standardize(para["name"])
        name = change_name(name)
        param_type = map_type.get(para["type"], "string")
        prompt = {
            "type": param_type,
            "description": para["description"][:description_max_length]
        }

        default_value = para['default']
        if len(str(default_value)) != 0:    
            prompt["example_value"] = default_value

        template["parameters"]["properties"][name] = prompt
        template["parameters"]["optional"].append(name)

    return template, api_json["category_name"], pure_api_name

# 获取工具白名单
def get_white_list(tool_root_dir):
    white_list_dir = os.path.join(tool_root_dir)
    white_list = {}
    for cate in tqdm(os.listdir(white_list_dir)):
        if not os.path.isdir(os.path.join(white_list_dir, cate)):
            continue
        for file in os.listdir(os.path.join(white_list_dir, cate)):
            if not file.endswith(".json"):
                continue
            standard_tool_name = file.split(".")[0]
            with open(os.path.join(white_list_dir, cate, file)) as reader:
                js_data = json.load(reader)
            origin_tool_name = js_data["tool_name"]
            white_list[standardize(origin_tool_name)] = {"description": js_data["tool_description"], "standard_tool_name": standard_tool_name}
    return white_list

# 检索 RapidAPI 工具
def retrieve_rapidapi_tools(query, top_k, jsons_path, retriever):
    retrieved_tools = retriever.retrieving(query, top_k=top_k)
    query_json = {"api_list": []}
    for tool_dict in retrieved_tools:
        if len(query_json["api_list"]) == top_k:
            break
        category = tool_dict["category"]
        tool_name = tool_dict["tool_name"]
        api_name = tool_dict["api_name"]
        if os.path.exists(jsons_path):
            if os.path.exists(os.path.join(jsons_path, category)):
                if os.path.exists(os.path.join(jsons_path, category, tool_name + ".json")):
                    query_json["api_list"].append({
                        "category_name": category,
                        "tool_name": tool_name,
                        "api_name": api_name
                    })
    return query_json

# 获取 API JSON 数据
def fetch_api_json(query_json, tool_root_dir):
    data_dict = {"api_list": []}
    for item in query_json["api_list"]:
        cate_name = item["category_name"]
        tool_name = standardize(item["tool_name"])
        api_name = change_name(standardize(item["api_name"]))
        tool_json = json.load(open(os.path.join(tool_root_dir, cate_name, tool_name + ".json"), "r"))
        for api_dict in tool_json["api_list"]:

            if change_name(standardize(api_dict["name"])) == api_name:
                api_json = {
                    "category_name": cate_name,
                    "api_name": api_dict["name"],
                    "api_description": api_dict["description"],
                    "required_parameters": api_dict["required_parameters"],
                    "optional_parameters": api_dict["optional_parameters"],
                    "tool_name": tool_json["tool_name"]
                }
                data_dict["api_list"].append(api_json)
                break
    return data_dict

# 构建工具描述
def build_tool_description(data_dict, tool_root_dir):
    white_list = get_white_list(tool_root_dir)
    origin_tool_names = [standardize(cont["tool_name"]) for cont in data_dict["api_list"]]
    tool_des = contain(origin_tool_names, white_list)
    tool_descriptions = [[cont["standard_tool_name"], cont["description"]] for cont in tool_des]
    return tool_descriptions

# 主运行函数
def run():
    parser = argparse.ArgumentParser(description="Retrieve tools and generate function descriptions.")
    parser.add_argument("--corpus_tsv_path", type=str, required=True, help="Path to the corpus TSV file.")
    parser.add_argument("--retrieval_model_path", type=str, required=True, help="Path to the retrieval model.")
    parser.add_argument("--input_file", type=str, required=True, help="Path to input file with queries.")
    parser.add_argument("--output_path", type=str, required=True, help="Path to output JSON file.")
    parser.add_argument("--top_k", type=int, default=5, help="Top K tools to retrieve.")
    parser.add_argument("--tool_root_dir", type=str, required=True, help="Root directory of tools.")
    args = parser.parse_args()

    retriever = ToolRetriever(corpus_tsv_path=args.corpus_tsv_path, model_path=args.retrieval_model_path)

    # 加载输入文件
    with open(args.input_file, 'r') as f:
        data = json.load(f)

    output_data = []

    # 逐个查询并处理
    for d in data:
        try:
            query = d["instruction"]
            query_json = retrieve_rapidapi_tools(query, args.top_k, args.tool_root_dir, retriever)
            data_dict = fetch_api_json(query_json, args.tool_root_dir)
            tool_descriptions = build_tool_description(data_dict, args.tool_root_dir)

            functions = []
            for k, api_json in enumerate(data_dict["api_list"]):
                standard_tool_name = tool_descriptions[k][0]
                openai_function_json, cate_name, pure_api_name = api_json_to_openai_json(api_json, standard_tool_name)
                functions.append(openai_function_json)

            finish_func = {
                "name": "Finish",
                "description": "If you believe that you have obtained a result that can answer the task, please call this function...",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "return_type": {
                            "type": "string",
                            "enum": ["give_answer", "give_up_and_restart"]
                        },
                        "final_answer": {
                            "type": "string",
                            "description": "The final answer you want to give the user."
                        }
                    },
                    "required": ["return_type"]
                }
            }

            functions.append(finish_func)
            task_description = f"You should use functions to help handle the real time user queries.\n"
            for k, (standardize_tool_name, tool_des) in enumerate(tool_descriptions):
                processed_tool_des = tool_des[:512].replace('\n', '').strip()
                task_description += f"{k + 1}. {standardize_tool_name}: {processed_tool_des}\n"

            # 保存到 JSON 结构
            output_data.append({
                "instruction": d["instruction"],
                "functions": functions,
                "task_description": task_description
            })
        except Exception as e:
            print(f"Error processing instruction: {d['instruction']}")
            print(f"Error: {e}")

    # 将结果保存到 JSON 文件
    with open(args.output_path, 'w') as outfile:
        json.dump(output_data, outfile, indent=4)


if __name__ == "__main__":
    run()
