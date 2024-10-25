import openai
import time

# 设置 API 基本信息
openai.api_base = "https://api.chatanywhere.com.cn/v1"
openai.api_key = "sk-GetueENFxFgzSXBFrMK7XyjPJtyz7oIyOjmYnpIZJHV4gldw"

def generate_data(prompt, model_name):
    temperature = 1
    retry_count = 5
    retry_interval = 1  # 单位是秒
    model_engine = 'gpt-4o-mini'  # 假设你要使用的模型
    for _ in range(retry_count):
        try:
            if model_name == 'openai':
                # 使用 OpenAI 的 ChatCompletion.create 方法来生成对话
                completion = openai.ChatCompletion.create(
                    model=model_engine,
                    messages=[
                        {"role": "system", "content": "You are a research assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                )
                # 返回生成的结果
                return completion.choices[0].message['content']
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(retry_interval)
    return "Failed to generate data after retries."

# # 示例调用
# result = generate_data("帮我生成一个关于能源转型的研究报告", "openai")
# print(result)
