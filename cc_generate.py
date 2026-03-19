#!/usr/bin/env python3
"""
cc_generate.py — 读取 data/claude.yaml，生成 zsh 和 bash 补全脚本
"""

import os
import sys
from pathlib import Path

import yaml

# ── 颜色支持 ──────────────────────────────────────────────────────
_COLOR = sys.stdout.isatty() and "NO_COLOR" not in os.environ


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _COLOR else text


def bold(s):   return _c("1", s)
def dim(s):    return _c("2", s)
def green(s):  return _c("32", s)
def yellow(s): return _c("33", s)
def cyan(s):   return _c("36", s)
def blue(s):   return _c("34", s)


def load_data() -> dict:
    """读取 data/claude.yaml"""
    data_file = Path(__file__).parent / "data" / "claude.yaml"
    if not data_file.exists():
        raise FileNotFoundError(
            f"  ❌ 找不到数据文件：{data_file}\n  请先运行：python cc_scan.py"
        )
    with open(data_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ─────────────────────────── zsh 生成 ───────────────────────────

def _zsh_escape(s: str) -> str:
    """转义 zsh 字符串中的特殊字符"""
    return s.replace("'", "'\\''").replace("[", "\\[").replace("]", "\\]").replace(":", "\\:")


def _zsh_func_name(cmd_path: list[str]) -> str:
    """生成 zsh 补全函数名，如 ['claude', 'auth', 'login'] → _claude_auth_login"""
    return "_" + "_".join(cmd_path)


def generate_zsh(node: dict, cmd_path: list[str] | None = None) -> list[str]:
    """
    递归生成 zsh 补全函数列表。
    返回 list[str]，每个元素是一个完整的函数定义。
    """
    if cmd_path is None:
        cmd_path = [node["name"]]

    func_name = _zsh_func_name(cmd_path)
    options = node.get("options", []) or []
    commands = node.get("commands", []) or []

    lines = []
    lines.append(f"{func_name}() {{")
    lines.append("  local context state state_descr line")
    lines.append("  typeset -A opt_args")
    lines.append("")
    lines.append("  _arguments -C \\")

    # 生成选项参数
    for opt in options:
        flags = opt.get("flags", [])
        desc = _zsh_escape(opt.get("description", ""))
        if not flags:
            continue
        if len(flags) == 1:
            flag = flags[0]
            lines.append(f"    '{flag}[{desc}]' \\")
        else:
            flags_str = ",".join(flags)
            flags_group = "{" + flags_str + "}"
            lines.append(f"    '({flags_str})'{flags_group}'[{desc}]' \\")

    # 如果有子命令，添加 state 支持
    if commands:
        lines.append("    '1: :->command' \\")
        lines.append("    '*:: :->args' \\")
        lines.append("  && return 0")
        lines.append("")
        lines.append("  case $state in")
        lines.append("    command)")
        lines.append("      local -a subcommands")
        lines.append("      subcommands=(")
        for cmd in commands:
            name = cmd["name"]
            desc = _zsh_escape(cmd.get("description", ""))
            lines.append(f"        '{name}:{desc}'")
        lines.append("      )")
        lines.append("      _describe 'command' subcommands")
        lines.append("      ;;")
        lines.append("    args)")
        lines.append("      case $line[1] in")
        for cmd in commands:
            sub_name = cmd["name"]
            sub_func = _zsh_func_name(cmd_path + [sub_name])
            lines.append(f"        {sub_name})")
            lines.append(f"          {sub_func}")
            lines.append("          ;;")
        lines.append("      esac")
        lines.append("      ;;")
        lines.append("  esac")
    else:
        lines.append("  && return 0")

    lines.append("}")
    lines.append("")

    # 递归生成子命令函数
    all_funcs = ["\n".join(lines)]
    for cmd in commands:
        sub_path = cmd_path + [cmd["name"]]
        all_funcs.extend(generate_zsh(cmd, sub_path))

    return all_funcs


def build_zsh_script(root: dict) -> str:
    """构建完整的 zsh 补全脚本"""
    root_name = root["name"]
    lines = [
        f"#compdef {root_name}",
        f"# zsh completion for {root_name}",
        f"# 由 cc_generate.py 自动生成",
        f"# 用法：将此文件放入 $fpath 目录（如 ~/.zsh/completions/），然后运行 compinit",
        "",
    ]

    funcs = generate_zsh(root)
    lines.extend(funcs)

    # 最后注册顶层函数
    lines.append(f"_{root_name}")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────── bash 生成 ───────────────────────────

def _collect_bash_cases(node: dict, cmd_path: list[str]) -> list[tuple[str, list[str]]]:
    """
    收集所有命令路径及其可补全项（选项 + 子命令）。
    返回 list[(case_key, completions)]
    """
    results = []
    options = node.get("options", []) or []
    commands = node.get("commands", []) or []

    # 当前节点的补全项
    completions = []
    for opt in options:
        completions.extend(opt.get("flags", []))
    for cmd in commands:
        completions.append(cmd["name"])

    if completions:
        # case key：对于顶层用 "claude"，子命令用最后一个命令名
        case_key = cmd_path[-1] if len(cmd_path) > 1 else cmd_path[0]
        results.append((case_key, completions))

    # 递归处理子命令
    for cmd in commands:
        sub_path = cmd_path + [cmd["name"]]
        results.extend(_collect_bash_cases(cmd, sub_path))

    return results


def build_bash_script(root: dict) -> str:
    """构建完整的 bash 补全脚本"""
    root_name = root["name"]
    cases = _collect_bash_cases(root, [root_name])

    lines = [
        f"# bash completion for {root_name}",
        f"# 由 cc_generate.py 自动生成",
        f"# 用法：在 ~/.bashrc 中添加：source /path/to/claude.bash",
        "",
        f"_{root_name}_completions() {{",
        "  local cur prev words cword",
        "  _init_completion 2>/dev/null || {",
        "    COMPREPLY=()",
        "    cur=\"${COMP_WORDS[COMP_CWORD]}\"",
        "    prev=\"${COMP_WORDS[COMP_CWORD-1]}\"",
        "  }",
        "",
        "  # 找出当前使用的子命令",
        "  local cmd=\"\"",
        "  local i",
        "  for ((i=1; i < COMP_CWORD; i++)); do",
        "    if [[ \"${COMP_WORDS[i]}\" != -* ]]; then",
        "      cmd=\"${COMP_WORDS[i]}\"",
        "      break",
        "    fi",
        "  done",
        "",
        "  case \"$cmd\" in",
    ]

    # 添加子命令的 case（跳过顶层，因为顶层在 default 处理）
    for case_key, completions in cases[1:]:
        completions_str = " ".join(completions)
        lines.append(f"    {case_key})")
        lines.append(f"      COMPREPLY=( $(compgen -W '{completions_str}' -- \"$cur\") )")
        lines.append("      return 0")
        lines.append("      ;;")

    # 默认（顶层命令）
    if cases:
        top_completions_str = " ".join(cases[0][1])
    else:
        top_completions_str = ""

    lines.append("    *)")
    lines.append(f"      COMPREPLY=( $(compgen -W '{top_completions_str}' -- \"$cur\") )")
    lines.append("      return 0")
    lines.append("      ;;")
    lines.append("  esac")
    lines.append("}")
    lines.append("")
    lines.append(f"complete -F _{root_name}_completions {root_name}")
    lines.append("")

    return "\n".join(lines)


# ─────────────────────────── main ───────────────────────────

def main():
    print(f"\n{bold('⚙️  生成补全脚本')}\n")
    print(f"  {dim('📖')} 读取命令树数据... ", end="", flush=True)
    root = load_data()
    print(green("完成"))

    output_dir = Path(__file__).parent / "completions"
    output_dir.mkdir(exist_ok=True)

    # 生成 zsh 补全脚本
    zsh_script = build_zsh_script(root)
    zsh_file = output_dir / "_claude"
    with open(zsh_file, "w", encoding="utf-8") as f:
        f.write(zsh_script)
    zsh_lines = zsh_script.count("\n")
    print(f"  {green('✅')} zsh  → {bold(str(zsh_file))}  {dim(f'({zsh_lines} 行)')}")

    # 生成 bash 补全脚本
    bash_script = build_bash_script(root)
    bash_file = output_dir / "claude.bash"
    with open(bash_file, "w", encoding="utf-8") as f:
        f.write(bash_script)
    bash_lines = bash_script.count("\n")
    print(f"  {green('✅')} bash → {bold(str(bash_file))}  {dim(f'({bash_lines} 行)')}")

    print(f"\n{bold('🎉 生成完成！')}\n")

    # 安装说明
    sep = dim("─" * 40)
    print(f"  {cyan(bold('zsh 安装方式'))}")
    print(f"  {sep}")
    print(f"  {dim('$')} mkdir -p ~/.zsh/completions")
    print(f"  {dim('$')} cp {zsh_file} ~/.zsh/completions/")
    print(f"  {dim('$')} echo {yellow(repr('fpath=(~/.zsh/completions $fpath)'))} >> ~/.zshrc")
    print(f"  {dim('$')} echo {yellow(repr('autoload -U compinit && compinit'))} >> ~/.zshrc")
    print()
    print(f"  {cyan(bold('bash 安装方式'))}")
    print(f"  {sep}")
    print(f"  {dim('$')} echo {yellow(repr(f'source {bash_file}'))} >> ~/.bashrc")
    print()


if __name__ == "__main__":
    main()
