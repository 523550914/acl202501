import json
import argparse
import os

def calculate_precision_recall(gt_list, re_list):
    # 计算交集
    true_positive = len(set(gt_list) & set(re_list))
    
    # 计算Precision (精确度)
    if len(re_list) > 0:
        precision = true_positive / len(re_list)
    else:
        precision = 0.0
    
    # 计算Recall (召回率)
    if len(gt_list) > 0:
        recall = true_positive / len(gt_list)
    else:
        recall = 0.0
    
    return precision, recall, true_positive, len(re_list), len(gt_list)

def main():
    # 设置参数解析器
    parser = argparse.ArgumentParser(description="计算汇总的精确度和召回率并保存到文件")
    parser.add_argument("--input_file", type=str, required=True, help="Ground truth 数据文件的路径")
    parser.add_argument("--retriever_file", type=str, required=True, help="预测数据文件的路径")
    parser.add_argument("--output_file", type=str, required=True, help="保存结果的文件路径（不包含 _topk）")
    parser.add_argument("--top_k", type=int, default=5, help="Top K 值，用于记录")
    args = parser.parse_args()


    # 打开并读取输入文件
    with open(args.input_file, 'r') as gt_f:
        gt_data = json.load(gt_f)
    with open(args.retriever_file, 'r') as re_f:
        pred_data = json.load(re_f)

    # 初始化累积值
    total_true_positive = 0
    total_re_list_len = 0
    total_gt_list_len = 0

    # 结果列表
    results = []
    
    # 循环遍历所有数据
    for i in range(len(pred_data)):
        query = pred_data[i]["instruction"]
        find = 0
        for j in range(len(gt_data)):
            if  gt_data[j]["instruction"] in query:
                
        # 提取ground truth和预测的工具列表
                gt_list = [tool["Name"] for tool in gt_data[j]["tools"]]
                re_list = [func["name"] for func in pred_data[i]["functions"]]
                
        # 计算每个条目的 Precision 和 Recall
                precision, recall, true_positive, re_len, gt_len = calculate_precision_recall(gt_list, re_list[:-1])
                
                # 累积每个条目的值
                total_true_positive += true_positive
                total_re_list_len += re_len
                total_gt_list_len += gt_len
                find = 1
                # total_true_positive += 1
                # total_re_list_len += 1
                # total_gt_list_len += 1
        # 保存每个条目的结果
                results.append({
                    "query": query,
                    "gt_list":gt_list,
                    "re_list":re_list[:-1],
                    "precision": round(precision, 2),
                    "recall": round(recall, 2),
                    "ground_truth_count": gt_len,
                    "retrieved_count": re_len
                })
        if find == 0:
            print(query)
            break
    
    # 计算汇总的 Precision 和 Recall
    if total_re_list_len > 0:
        overall_precision = total_true_positive / total_re_list_len
    else:
        overall_precision = 0.0

    if total_gt_list_len > 0:
        overall_recall = total_true_positive / total_gt_list_len
    else:
        overall_recall = 0.0

    # 保存汇总结果
    summary = {
        "overall_precision": round(overall_precision, 2),
        "overall_recall": round(overall_recall, 2),
        "total_ground_truth_count": total_gt_list_len,
        "total_retrieved_count": total_re_list_len,
        "top_k": args.top_k
    }

    # 将结果保存到指定的文件，路径包含 "_topk"
    output_data = {
        "item_results": results,
        "summary": summary
    }

    with open(args.output_file,'w') as outfile:
        json.dump(output_data, outfile, indent=4)
    
    print(f"结果已保存到 {args.output_file}")

if __name__ == "__main__":
    main()
