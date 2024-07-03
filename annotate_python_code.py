import ast
import os
from simpleaichat.simpleaichat import AIChat

def add_comments_to_code(code, ai):
    code_with_comment_chain_systemtemplate = """
    你强大的人工智能 Code Commenter。

    你的任务是为python每一行代码增加中文注释。以及增加文档注释。禁止修改代码！

    只允许输出增加注释后的python代码。禁止输出任何其他内容！

    """
    last_response = ""  # 初始化上一次的输出为空字符串
    response_td = None

    for chunk in ai.stream(code, id="code_commenter", system=code_with_comment_chain_systemtemplate):
        response_td = chunk["response"]
        if response_td.startswith(last_response):
            # 只输出新的部分
            new_content = response_td[len(last_response):]
            print(new_content, end='')
        else:
            # 输出完整的新内容
            print(response_td, end='')
        last_response = response_td  # 更新上一次的输出
    return response_td

def process_file(file_path, output_dir, ai):
    with open(file_path, 'r', encoding='utf-8') as file:
        code = file.read()

    tree = ast.parse(code)

    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

    commented_code = ""
    # 遍历所有函数定义
    for function in functions:
        # 获取函数定义的源代码
        function_source = ast.get_source_segment(code, function)
        commented_code_td = add_comments_to_code(function_source, ai)
        commented_code += commented_code_td

    os.makedirs(output_dir, exist_ok=True)

    # 保存结果到目标文件
    output_file_path = os.path.join(output_dir, os.path.basename(file_path)+'.md')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(commented_code)


def process_directory(start_dir, output_dir, ai):
    for root, _, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                # 创建输出文件路径
                rel_path = os.path.relpath(file_path, start_dir)
                output_file_path = os.path.join(output_dir, rel_path)

                # 检查输出文件是否已存在
                if os.path.exists(output_file_path):
                    print(f"Skipping {file_path} as it already exists in output directory.")
                    continue

                output_path = os.path.dirname(output_file_path)
                process_file(file_path, output_path, ai)


if __name__ == "__main__":
    input_directory = '/home/touka/PycharmProjects/MMIN'
    output_directory = '/home/touka/PycharmProjects/Added'

    # 设置API参数
    params = {"temperature": 0.1, "max_tokens": 2000}  # 适当调整max_tokens以满足你的需求
    model = "qwen-turbo"
    ai = AIChat(id="code_commenter", model=model, params=params, save_messages=False, console=False)

    process_directory(input_directory, output_directory, ai)
