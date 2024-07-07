# Code Comment Generator

## 简介
Code Comment Generator用于自动为Python代码文件添加中文注释。使用`simpleaichat`库与LLM交互，以生成注释。

## 特点
- 自动生成中文注释和文档注释。
- 支持处理大型代码文件，通过分块处理。
- 将注释后的代码保存为Markdown和Python文件。

## 安装
在开始使用之前，请确保您的系统上安装了以下依赖项：
- Python 3.x
- `tree_sitter_python`
- `semantic_text_splitter`
- `simpleaichat`

您可以通过以下命令安装所需的Python包：
```bash
pip install tree_sitter tree_sitter_python semantic_text_splitter simpleaichat
```

## 使用方法
1. 克隆本项目或下载压缩包并解压。
2. 使用命令行工具，导航到项目目录。
3. 运行脚本并提供输入和输出目录，以及其他可选参数。

以下是运行脚本的命令行示例：
```bash
python comment_gen.py <input_directory> <output_directory> --temperature <value> --max_tokens <value> --model <model_name> --base_url <base_url>
```
- `<input_directory>`: 包含Python文件的目录。
- `<output_directory>`: 保存处理后文件的目录。
- `--temperature`: AI模型的温度参数，默认为0.4。
- `--max_tokens`: AI模型的最大令牌数参数，默认为2000。
- `--model`: 使用的AI模型名称，默认为"qwen-turbo"。
- `--base_url`: AI服务的基础URL，默认为"https://dashscope.aliyuncs.com/compatible-mode/v1"。

## 示例
以下是如何使用脚本的示例：

```bash
python comment_gen.py ./src ./out --temperature 0.5 --max_tokens 2500 --model qwen-turbo --base_url https://api.example.com
```

## 输出
处理完成后，脚本将在指定的输出目录中生成以下文件：
- Markdown文件：包含注释的代码。
- Python文件：仅包含处理后的Python代码块。

## 注意事项
- 确保输入的Python代码文件使用UTF-8编码。
- 脚本不会修改原始代码，只会添加注释。

## 贡献
如果您有任何建议或想要贡献代码，请提交Pull Request或创建Issue。

## 许可
本项目采用[MIT许可](LICENSE)。
