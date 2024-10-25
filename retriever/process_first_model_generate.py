import json


input_file = '/dat03/zly/ToolPlanner/output/first_sentence_model/G3/sft/inference_output/generated_new_query.json'
output_file = '/dat03/zly/ToolPlanner/zly_data/retriever/G3/first_model_generate/test.query.txt'

with open(input_file, 'r') as in_f:
    in_data = json.load(in_f)
    for d in in_data:
        id = d['id']
        query = d['new_output']
        if '\n' in query:
            continue
            query = query.split('\n')[0]
            print(id)
        
        
        with open(output_file, 'a') as out_f:
            out_f.write(f"{id}\t{query}\n")  # 按指定格式写入 id 和 new_output
        