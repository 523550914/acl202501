hybrid_query_path = "/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/hybrid/train.query.txt"
state_output_path = "/dat03/zly/ToolPlanner/data/toolbench/retrieval/G3/state/train.query.txt"

def extract_sentence_after_number(text):
    # 找到数字和第一个句号或问号的位置
    sentence = ""
    split_text = text.split("\t")
    if len(split_text) > 1:
        sentence_part = split_text[1].strip()  # 获取数字之后的部分
        # 找到第一个句号或问号
        end_pos = min(
            sentence_part.find('.'),
            sentence_part.find('?')
        )
        # 如果句号或问号不存在，则返回整个句子
        if end_pos == -1:
            sentence = sentence_part
        else:
            sentence = sentence_part[:end_pos + 1]
    return sentence

# 读取 hybrid_queries 并提取目标部分
with open(hybrid_query_path, "r") as h_f:
    hybrid_queries = h_f.readlines()

# 打开 state 文件用于写入
with open(state_output_path, "w") as state_f:
    # 遍历每一行并提取句子和序号
    for query in hybrid_queries:
        # 提取序号和句子
        split_query = query.split("\t")
        if len(split_query) > 1:
            sentence = extract_sentence_after_number(query)
            if sentence:
                # 保存序号和提取的句子到 state 文件
                state_f.write(f"{split_query[0]}\t{sentence}\n")

print(f"提取结果已保存到 {state_output_path}")
