import json
import argparse
import pickle
import pandas as pd
from vllm import LLM, SamplingParams

def main(args):
    # Define sampling parameters from the parsed arguments
    sampling_params = SamplingParams(temperature=args.temperature, n=args.n, max_tokens=args.max_tokens)

    # Initialize LLM with model path and parallelization setting
    llm = LLM(
        model=args.model_path,
        trust_remote_code=True,
        tokenizer=args.model_path,
        dtype='bfloat16',
        tokenizer_mode='auto',
        tensor_parallel_size=args.tensor_parallel_size,
        gpu_memory_utilization=0.8,

    )

    # Read input data from JSON file
    prompts = []
    with open(args.input_file, 'r') as f:
        test_data = json.load(f)
        for i in range(len(test_data)):
            text = test_data[i]["instruction"]
            prompts.append(f"<s> [INST] {text} [/INST]")
            
    # Generate outputs
    outputs = llm.generate(prompts, sampling_params)
    print(outputs[0])
    results = []
    for i in range(len(outputs)):
        result = {
            "id":test_data[i]["id"],
            "orig_output": test_data[i]["output"],
            "instruction": test_data[i]["instruction"],
            "new_output": outputs[i].outputs[0].text
        }
        results.append(result)
    # Save the outputs to a file (pickle format for convenience)
    with open(args.output_file, 'w') as f:

        json.dump(results, f, ensure_ascii=False, indent=4)

    print(f"Generated outputs saved to {args.output_file}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run LLM with specified parameters")
    parser.add_argument('--model_path', type=str, required=True, help='Path to the model')
    parser.add_argument('--input_file', type=str, required=True, help='Path to the input JSON file')
    parser.add_argument('--output_file', type=str, required=True, help='Path to save the output file')
    parser.add_argument('--tensor_parallel_size', type=int, default=1, help='Number of parallel tensor slices')
    parser.add_argument('--temperature', type=float, default=0, help='Sampling temperature')
    parser.add_argument('--n', type=int, default=1, help='Number of output sequences to generate')
    parser.add_argument('--max_tokens', type=int, default=2048, help='Maximum number of tokens to generate')

    args = parser.parse_args()
    main(args)
