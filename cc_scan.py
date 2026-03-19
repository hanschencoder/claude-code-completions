#!/usr/bin/env python3
"""
cc_scan.py — 递归扫描 claude CLI 命令树，输出 data/claude.yaml
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ── 颜色支持 ──────────────────────────────────────────────────────
_COLOR = sys.stderr.isatty() and "NO_COLOR" not in os.environ


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def bold(s):   return _c("1", s)
def dim(s):    return _c("2", s)
def red(s):    return _c("31", s)
def green(s):  return _c("32", s)
def yellow(s): return _c("33", s)
def cyan(s):   return _c("36", s)


def run_help(cmd_path: list[str]) -> str:
    """执行 claude [subcmds...] --help，返回输出（超时 5 秒）"""
    cmd = cmd_path + ["--help"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = result.stdout
        if not output:
            output = result.stderr
        return output
    except subprocess.TimeoutExpired:
        indent = "  " * len(cmd_path)
        print(f"{indent}{yellow('⏱')}  {dim('超时：')} {yellow(' '.join(cmd))}", file=sys.stderr)
        return ""
    except FileNotFoundError:
        print(f"  {red('❌')} 找不到命令：{red(cmd[0])}", file=sys.stderr)
        return ""


def parse_options(text: str) -> list[dict]:
    """解析 Options 段，提取 flags 列表和描述"""
    options = []
    in_options = False

    for line in text.splitlines():
        # 检测 section header：只有无缩进的行才算（排除 Examples: 等嵌入标题）
        stripped = line.strip()
        if not line.startswith(" ") and re.match(r'^[A-Z][a-zA-Z ]*:$', stripped):
            in_options = stripped.lower().startswith("option")
            continue

        if not in_options:
            continue

        # 匹配选项行：2+ 空格开头，flags，可选参数占位符（单空格分隔），2+ 空格，描述
        # 用单个 \s 而非 \s+ 匹配占位符前的空格，避免吃掉 2+ 空格分隔符
        m = re.match(r'^\s{2,}(-[^\s,]+(?:,\s*-[^\s,]+)*)(?:\s\S+)*\s{2,}(.+)$', line)
        if m:
            flags_str, description = m.group(1), m.group(2).strip()
            # 拆分多个 flag，如 "-h, --help" → ["-h", "--help"]
            flags = [f.strip() for f in flags_str.split(",")]
            # 过滤掉带参数占位符的部分（如 "--output <file>"）
            clean_flags = []
            for f in flags:
                parts = f.split()
                if not parts:
                    continue
                flag_part = parts[0]
                if flag_part.startswith("-"):
                    clean_flags.append(flag_part)
            if clean_flags:
                options.append({"flags": clean_flags, "description": description})

    return options


def parse_commands(text: str) -> list[dict]:
    """解析 Commands 段，提取子命令名称和描述"""
    commands = []
    in_commands = False

    for line in text.splitlines():
        # 检测 section header：只有无缩进的行才算（排除 Examples: 等嵌入标题）
        stripped = line.strip()
        if not line.startswith(" ") and re.match(r'^[A-Z][a-zA-Z ]*:$', stripped):
            in_commands = stripped.lower().startswith("command")
            continue

        if not in_commands:
            continue

        # 用 2+ 空格做列分割：第一列是命令名（可能含 [options]、|alias 等），第二列是描述
        m = re.match(r'^\s{2,}(\S.*?)\s{2,}(.+)$', line)
        if m:
            name_part, description = m.group(1), m.group(2).strip()
            # 取第一个词（去掉 [options] 等），再按 | 拆分出所有别名
            first_word = name_part.split()[0]
            names = first_word.split("|")
            for name in names:
                if not re.match(r'^\w[\w-]*$', name):
                    continue
                commands.append({"name": name, "description": description})

    return commands


def scan_node(cmd_path: list[str], visited: set | None = None) -> dict:
    """递归扫描，构建节点字典"""
    if visited is None:
        visited = set()

    path_key = tuple(cmd_path)
    if path_key in visited:
        return {}
    visited.add(path_key)

    name = cmd_path[-1]
    depth = len(cmd_path)
    indent = "  " * depth
    print(f"{indent}{dim('▸')} {cyan(name)}", file=sys.stderr)

    help_text = run_help(cmd_path)
    options = parse_options(help_text)
    sub_cmds_info = parse_commands(help_text)

    sub_nodes = []
    for cmd_info in sub_cmds_info:
        sub_name = cmd_info["name"]
        sub_path = cmd_path + [sub_name]
        sub_key = tuple(sub_path)

        if sub_key in visited:
            continue

        # help 是内置伪命令，不需要递归扫描，直接作为叶节点
        if sub_name == "help":
            sub_nodes.append({
                "name": "help",
                "description": cmd_info["description"],
                "options": [],
                "commands": [],
            })
            continue

        sub_node = scan_node(sub_path, visited)
        if sub_node:
            # 如果扫描结果没有描述，用解析到的描述补充
            if not sub_node.get("description"):
                sub_node["description"] = cmd_info["description"]
            sub_nodes.append(sub_node)
        else:
            # 扫描失败，用基本信息填充
            sub_nodes.append({
                "name": sub_name,
                "description": cmd_info["description"],
                "options": [],
                "commands": [],
            })

    # 从 help 文本提取描述（通常是第一行非空行）
    description = ""
    for line in help_text.splitlines():
        line = line.strip()
        if line and not line.startswith("-") and not line.lower().startswith("usage"):
            description = line
            break

    return {
        "name": name,
        "description": description,
        "options": options,
        "commands": sub_nodes,
    }


def main():
    print(f"\n{bold('🔍 开始扫描 claude CLI 命令树...')}\n", file=sys.stderr)

    # 检查 claude 是否可用
    try:
        subprocess.run(["claude", "--version"], capture_output=True, timeout=5)
    except FileNotFoundError:
        print(f"  {red('❌ 错误：')}找不到 claude 命令，请确保已安装 Claude Code CLI", file=sys.stderr)
        sys.exit(1)

    root = scan_node(["claude"])

    # 写入 YAML
    output_dir = Path(__file__).parent / "data"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "claude.yaml"

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(root, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    # 统计
    def count_nodes(node):
        total = 1
        for sub in node.get("commands", []):
            total += count_nodes(sub)
        return total

    total = count_nodes(root)
    print(f"\n  {green('✅')} 命令树已写入 {bold(str(output_file))}", file=sys.stderr)
    print(f"  {dim('📊')} 共扫描 {bold(str(total))} 个命令节点\n", file=sys.stderr)


if __name__ == "__main__":
    main()
