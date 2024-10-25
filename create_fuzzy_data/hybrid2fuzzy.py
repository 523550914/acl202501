import json
fuzzy_file='/dat03/zly/ToolPlanner/zly_data/retriever/G3/fuzzy/test.json'
hybrid_text='/dat03/zly/ToolPlanner/zly_data/retriever/G3/hybrid/test.query.txt'
output_file='/dat03/zly/ToolPlanner/zly_data/retriever/G3/fuzzy/test.query.txt'
with open(fuzzy_file,'r') as f:
    fuzzy_data=json.load(f)
with open(hybrid_text,'r') as f:
    hybrid_data=f.readlines()
print('hybrid',len(hybrid_text))
print('fuzzy',len(fuzzy_data))
with open(output_file,'w') as output_f:

    for i,query in enumerate(hybrid_data):
        split_query = query.split("\t")
        sentence = fuzzy_data[i]['instruction']
        output_f.write(f"{split_query[0]}\t{sentence}\n")