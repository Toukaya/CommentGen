import argparse
import logging
import re
from pathlib import Path
from typing import Generator

import tree_sitter_python
from semantic_text_splitter import CodeSplitter

from simpleaichat.simpleaichat import AIChat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
System_prompt = """
你是一个专业的 Python 代码注释助手。

任务：
- 为每行 Python 代码添加详细的中文注释，解释功能和逻辑。
- 为函数和类添加用途和参数的文档注释。
- **只增加注释，不修改任何代码，包括空格和缩进**。

输出：
- 输出注释后的完整代码。
- 仅输出代码和注释，不要输出其他内容。

请处理以下 Python 代码。
"""


def get_split_chunks(max_chars: int, code: str, language) -> Generator[str, None, None]:
    """
    Split the code into chunks that do not exceed max_chars using the given language for parsing.
    Yields each chunk lazily.
    """
    code_splitter = CodeSplitter(language, max_chars, trim=False)
    for chunk in code_splitter.chunks(code):
        yield chunk


def extract_python_code_blocks(markdown_text: str) -> list[str]:
    """
    Extract Python code blocks from Markdown text using a regular expression.
    """
    pattern = r"```python\n(.*?)```"
    return re.findall(pattern, markdown_text, re.DOTALL)


def add_comments_to_code(code: str, ai: AIChat) -> str:
    chunk = None
    for chunk in ai.stream(code, id="code_commenter", system=System_prompt):
        delta = chunk["delta"]
        print(delta, end='')

    print('\n')
    return chunk["response"] + "\n\n"


def process_file(file_path: Path, output_dir: Path, ai: AIChat):
    """
    Process a single file, split it into chunks, add comments, and save the results.
    Handles large files by processing them in chunks.
    """
    try:
        with file_path.open('r', encoding='utf-8') as file:
            code = file.read()
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        return
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        return

    commented_code = ""
    for chunk in get_split_chunks(800, code, tree_sitter_python.language()):
        commented_code += add_comments_to_code(chunk, ai)

    save_markdown(commented_code, file_path, output_dir)
    save_processed_code(commented_code, file_path, output_dir)


def save_markdown(commented_code: str, file_path: Path, output_dir: Path):
    """
    Save the commented code as a markdown file.
    """
    output_file_path = output_dir / "markdown_file" / f"{file_path.name}.md"
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with output_file_path.open('w', encoding='utf-8') as file:
        file.write(commented_code)

    logging.info(f"Saved markdown to {output_file_path}")


def save_processed_code(commented_code: str, file_path: Path, output_dir: Path):
    """
    Extract Python code blocks from the commented markdown and save them as .py files.
    """
    processed_code = "\n".join(extract_python_code_blocks(commented_code))
    output_file_path = output_dir / file_path.name
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    with output_file_path.open('w', encoding='utf-8') as file:
        file.write(processed_code)

    logging.info(f"Saved processed code to {output_file_path}")


def process_directory(start_dir: Path, output_dir: Path, ai: AIChat, skip_dirs: list[Path] = None):
    """
    Process all Python files in a directory, add comments, and save the output.
    Uses Pathlib for path manipulations and logs each file processed.
    """
    for file_path in start_dir.rglob('*.py'):
        # 检查文件路径是否包含要跳过的文件夹名
        if any(Path(part) in skip_dirs for part in file_path.parents):
            logging.info(f"Skipping {file_path} as it is in a skipped directory.")
            continue
        rel_path = file_path.relative_to(start_dir)
        output_file_path = output_dir / rel_path

        if output_file_path.exists():
            logging.info(f"Skipping {file_path} as it already exists in the output directory.")
            continue

        process_file(file_path, output_file_path.parent, ai)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Python files to add comments.")
    parser.add_argument("input_directory", type=str, help="The input directory containing Python files.")
    parser.add_argument("output_directory", type=str, help="The output directory to save processed files.")
    parser.add_argument("--temperature", type=float, default=0.4, help="Temperature parameter for the AI model.")
    parser.add_argument("--max_tokens", type=int, default=2000, help="Max tokens parameter for the AI model.")
    parser.add_argument("--model", type=str, default="qwen-turbo", help="Model name for the AI.")
    parser.add_argument("--base_url", type=str, default="https://dashscope.aliyuncs.com/compatible-mode/v1",
                        help="Base URL for the AI service.")
    parser.add_argument("--skip_dirs", nargs="*", type=Path, default=[Path('.env')],
                        help="Directories to skip, separated by spaces.")

    args = parser.parse_args()
    input_directory = Path(args.input_directory)
    output_directory = Path(args.output_directory)

    ai = AIChat(
        id="code_commenter",
        model=args.model,
        params={
            "temperature": args.temperature,
            "max_tokens": args.max_tokens
        },
        save_messages=False,
        console=False,
        base_url=args.base_url
    )

    skip_dirs = [input_directory / Path(skip_dir) for skip_dir in args.skip_dirs]
    process_directory(
        input_directory,
        output_directory,
        ai,
        skip_dirs=skip_dirs
    )
    ai.delete_session(id="code_commenter")
    logging.info("Processing complete.")
