import json
import argparse

# 解析命令行参数
parser = argparse.ArgumentParser(description="Process input and output file paths.")
parser.add_argument("--input_file_path", type=str, required=True, help="The input JSON file path.")
parser.add_argument("--output_file_path", type=str, required=True, help="The output JSON file path.")
args = parser.parse_args()

# 从文件中读取数据
with open(args.input_file_path, "r") as f_in:
    data = json.load(f_in)
    
    # 修改每个数据的 instruction 字段
    for d in data:
        instruction_text = d["instruction"]

        # 查找第一个句号或问号的位置
        first_period_pos = instruction_text.find('.')
        first_question_pos = instruction_text.find('?')

        # 获取最近的句号或问号的位置
        cutoff_pos = min([pos for pos in [first_period_pos, first_question_pos] if pos != -1])

        # 截取到最近的句号或问号为止的字符串
        if cutoff_pos != -1:
            d["instruction"] = instruction_text[:cutoff_pos + 1]

        # 修改 conversation 中的值
        conversation = d["chains"]
        conversation[1]['value'] = "\n" + d["instruction"] + "\nBegin!\n"

# 将修改后的数据写入输出文件
with open(args.output_file_path, "w") as f_out:
    json.dump(data, f_out, indent=4)

print(f"已将修改后的数据保存到新文件: {args.output_file_path}")
