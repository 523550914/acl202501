import json
import argparse
import os
import re
import tqdm
# this code will reorganize the training data of toolbench into the conversation form, and change to tool document schema
def process_system_message(system_message, functions):
    assert "with a function call to actually excute your step." in system_message
    # we find that following ReACT format and merging the thought node and function call node is easier for model to learn to integrate the action input json string in its prediction than learn to predict a json string directly.
    system_message = system_message.replace("with a function call to actually excute your step.", "with a function call to actually excute your step. Your output should follow this format:\nThought:\nAction\nAction Input:\n")
    # add all the function dicts in the prompt.
    system_message = system_message + "\nSpecifically, you have access to the following APIs: " + str(functions)
    return system_message
def process_assistant_reply(message_dict: dict) -> str:
        content = message_dict["content"]
        if "function_call" in message_dict:
            function_call = message_dict["function_call"]
            reply = function_call # the whole dict containing action name and action input as target.
        elif content is not None:
            reply = content
        else:
            print(f"Wrong assistant reply: {message_dict}")
            return ""
        return reply
def change_relevant_tools(tools):
    new_tools = []
    for tool in tools:
        new_tool = ''.join(['_' if not c.isalnum() else c.lower() for c in tool[0]]) + '_for_' + ''.join(['_' if not c.isalnum() else c.lower() for c in tool[1]])
        # 输出结果

    new_tools.append(new_tool)
    return new_tools
def compute_similarity(tool_name_str, relevant_tool_slist):
    sim_list = []
    for relevant_tool_str in relevant_tool_slist:
    # 将字符串转为字符集合
        tool_set = set(tool_name_str)
        relevant_set = set(relevant_tool_str)

        # 计算交集
        intersection = tool_set.intersection(relevant_set)

        # 计算交集与两者长度的比例
        similarity_ratio = len(intersection) / min(len(tool_set), len(relevant_set))
        sim_list.append(similarity_ratio)
    return max(sim_list)
def prepro_conversation(functions,train_message,temple):
    conversations = []
    cur_react = ""
    if temple == "toolbench_backbone":
        for message_id, message_dict in enumerate(train_message):
            role = message_dict["role"]
            content = message_dict["content"]
            if role == "assistant":
                inputs = process_assistant_reply(message_dict) 
                
                # process the last assistant message as target
                if message_id + 1 == len(train_message):
                    if "function_call" not in message_dict:
                        cur_react = ""
                        break
                    else:
                        if cur_react == "":
                            cur_react += "\nThought: "
                        action = inputs["name"]
                        action_input = inputs["arguments"]
                        cur_react += f"\nAction: {action}"
                        cur_react += f"\nAction Input: {action_input}"
                        conversations.append({
                            "from": role,
                            "value": cur_react
                        })
                        cur_react = ""     
                    break
                else:
                    if "function_call" not in message_dict:
                        cur_react += f"\nThought: {inputs}"
                        continue
                    else:
                        if cur_react == "":
                            cur_react += "\nThought: "
                        action = inputs["name"]
                        action_input = inputs["arguments"]
                        cur_react += f"\nAction: {action}"
                        cur_react += f"\nAction Input: {action_input}"
                        conversations.append({
                            "from": role,
                            "value": cur_react
                        })
                        cur_react = ""
            elif role != "system":
                
                inputs = content
                conversations.append({
                    "from": role,
                    "value": inputs
                })
                cur_react = ""    
        return conversations
    elif temple == "toolbench_toolllama":
        for message_id, message_dict in enumerate(train_message):
            role = message_dict["role"]
            content = message_dict["content"]
            if role == "assistant":
                inputs = process_assistant_reply(message_dict) 
                
                # process the last assistant message as target
                if message_id + 1 == len(train_message):
                    if "function_call" not in message_dict:
                        cur_react = ""
                        break
                    else:
                        if cur_react == "":
                            cur_react += "\nThought: "
                        action = inputs["name"]
                        action_input = inputs["arguments"]
                        cur_react += f"\nAction: {action}"
                        cur_react += f"\nAction Input: {action_input}"
                        conversations.append({
                            "from": role,
                            "value": cur_react
                        })
                        cur_react = ""     
                    break

                # process the former assistant messages into history conversations
                else:
                    if "function_call" not in message_dict:
                        cur_react += f"\nThought: {inputs}"
                        continue
                    else:
                        if cur_react == "":
                            cur_react += "\nThought: "
                        action = inputs["name"]
                        action_input = inputs["arguments"]
                        cur_react += f"\nAction: {action}"
                        cur_react += f"\nAction Input: {action_input}"
                        conversations.append({
                            "from": role,
                            "value": cur_react
                        })
                        cur_react = ""
            else:
                if role == "system":
                    inputs = process_system_message(content, functions)
                else:
                    inputs = content
                conversations.append({
                    "from": role,
                    "value": inputs
                })
                cur_react = ""    
     
        return conversations
print("####################### PREPRO RAW DATA STAGE 1 #####################")

parser = argparse.ArgumentParser()
parser.add_argument('--all_query_file', type=str, default="/dat03/zly/ToolPlanner/data/toolbench/instruction/G3_query.json")
parser.add_argument('--test_query_file', type=str, default="/dat03/zly/ToolPlanner/data/toolbench/test_query_ids/G3_instruction_test_query_ids.json")
parser.add_argument('--data_dir', type=str, default="/dat03/zly/ToolPlanner/code/Multi-LLM-Agent/data/toolbench")
parser.add_argument('--output_dir', type=str, default='/dat03/zly/ToolPlanner/zly_data/retriever/G3/hybrid/new_format')
parser.add_argument('--temple', type=str, default="toolbench_toolllama")
parser.add_argument('--test_ids')

args = parser.parse_args()


test_ids = []
# print(args.test_ids.split(','))
# for test_set in args.test_ids.split(','):
with open (args.test_query_file,'r') as f:
    data = json.load(f)
    test_ids += list(data.keys())
with open(args.all_query_file,'r') as f:
    all_query_data = json.load(f)
    

print('test_ids', test_ids)

data = []
for train_set in ["G3_answer"]:
    for file in tqdm.tqdm(os.listdir(f"{args.data_dir}/answer/{train_set}")):
        id = file.split('_')[0]
        # if id not in test_ids:
        if id in test_ids:
            with open(f"{args.data_dir}/answer/{train_set}/{file}") as f:
                d = json.load(f)
                
            if "answer_generation" in d.keys() and "train_messages" in d['answer_generation'].keys():
                instruction = d['answer_generation']['query']
                new_tools = []
                for t in d['answer_generation']['function']:
                    # tool_name = change_name(standardize(t['api_name'])) + '_for_' + standardize(t['tool_name'])
                    tool_name = t['name']
                    for all_query_d in all_query_data:
                        if int(all_query_d['query_id']) == int(id):
                            relevant_tools_str=''
                            relevant_tools = all_query_d['relevant APIs']
                            relevant_tools_list = change_relevant_tools(relevant_tools)
                            similarity = compute_similarity(tool_name, relevant_tools_list)
                            # if tool_name != "Finish" and similarity > 0.8:
                            if tool_name != "Finish":
                                print(tool_name)
                                tool_name = tool_name[-64:]
                                tool_function = t['description'][:256]
                                tool_input = {}
                                for arg_name,arg_value in t['parameters']['properties'].items():
                                    arg_type = arg_value['type']
                                    if 'description' in arg_value.keys():
                                        tool_input[arg_name] = arg_type + ', ' + arg_value['description'][-256:]
                                    else:
                                        tool_input[arg_name] = arg_type
                                # print(json.dumps(t, indent=2))
                                new_tools.append({
                                    'Name': tool_name,
                                    'function':tool_function,
                                    'input':tool_input
                                })
                function = d['answer_generation']['function']
                data.append({
                    'id':id,
                    'tools':new_tools,
                    'instruction':instruction,
                    'chains':prepro_conversation(function,d['answer_generation']['train_messages'][-1],args.temple)
                })

    print(train_set,'data processed')
            
os.makedirs(args.output_dir, exist_ok=True)
with open(f"{args.output_dir}/{args.temple}.json", 'w') as f:
    json.dump(data,f, indent=2)
