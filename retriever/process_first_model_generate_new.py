import json


input_file = '/dat03/zly/ToolPlanner/output/first_sentence_model/G3/sft/inference_output/generated_new_query.json'
orig_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/hybrid/new_format/toolbench_toolllama.json'

output_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/first_model_generate/new_format/toolbench_toolllama.json'
new_data_list=[]
with open(orig_file, 'r') as orig_f:
    orig_data = json.load(orig_f)
with open(input_file, 'r') as in_f:
    in_data = json.load(in_f)
    for d in in_data:
        query = d['new_output']
        new_data = {}
        if '\n' in query:
            continue
        orig = d['orig_output']
        
        for od in orig_data:
            if orig == od['instruction']:
                new_data['id'] = od['id']
                new_data['instruction'] = query
                new_data['tools']=od['tools']
                new_data['chains']=od['chains']
                new_data_list.append(new_data)
                break
with open(output_file, 'w') as out_f:
    json.dump(new_data_list, out_f, indent=4)
        

        