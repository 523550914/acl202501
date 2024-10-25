import json
import os
import re


def extract_right_path(node,path):
    filtered_node = {k: v for k, v in node.items() if k != 'children'}
    path.append(filtered_node)
    children = node['children']
    if children:
        extract_right_path(children[-1],path)

def extract_solution_path(path):
    solution_path = []
    i = 0
    for step in path:
        if step['node_type'] == 'Action':
            solution_path.append(f"{i+1}.{step['description']}"+'\n')
            i += 1
    return solution_path

def extract_tag_lists(instruction,id):
    tag_list= {}
    for data in instruction:
        if data['query_id'] == int(id):
            category_list = []
            for category_data in data['api_list']:
                if category_data['category_name'] not in category_list:
                    category_list.append(category_data['category_name'])
            tag_list['category'] = (',').join(category_list)
            tag_list['api'] = [api[1] for api in data['relevant APIs']]
            tag_list['tool'] = [api[0] for api in data['relevant APIs']]
            query = data['query']
    return tag_list,query


def converrt_path_to_conversation(query,right_path):
    conversation = []
    conversation.append({"from":"system","value":system_prompt})
    conversation.append({'from':'user','value':query})
    
    step_dict = {}
    step_dict['Thought']=''
    step_dict['Action']=''
    step_dict['Action Input']={}
    for i,step in enumerate(right_path):
        type = step['node_type']
        if type =='Thought':
            step_dict['Thought'] = step['description']
        elif type == 'Action':
            step_dict['Action'] = step['description']
        elif type == 'Action Input' and i != 0:
            step_dict['Action Input'] = step['description']
            conversation.append({'from':'assistant','value':f"\nThought:{step_dict['Thought']}\nAction:{step_dict['Action']}\nAction Input:{step_dict['Action Input']}"})
            step_dict['Thought']=''
            step_dict['Action']=''
            step_dict['Action Input']={}
            try:
                conversation.append({'from':'function','value':step['observation']})
            except:
                pass
            
    return conversation

def main():
    instruction_path = '/dat03/zly/ToolPlanner/data/toolbench/instruction/G3_query.json'
    with open(instruction_path,'r') as instruction_file, open('/dat03/zly/ToolPlanner/zly_data/retriever/G3/step2_data.json','w') as out_file:
        instruction = json.load(instruction_file)
        step2_data_list = []
        for data in instruction:
            step2_data = {}
            step2_data['id']= data['query_id']
            step2_data['tag_list'],step2_data['query'] = extract_tag_lists(instruction,data['query_id'])
            step2_data['orig_state_level'] = re.split(r'[.?]', step2_data['query'])[0] + '?'
            step2_data_list.append(step2_data)

        json.dump(step2_data_list,out_file,indent=4)
    print("stage2 data length",len(step2_data_list))
    print("orig data length",len(instruction))
if __name__ == "__main__":
    main()
