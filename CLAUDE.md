# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目说明

这是一个两阶段 Pipeline 工具，为 `claude` CLI 自动生成 zsh 和 bash 的 Tab 补全脚本。

## 常用命令

```bash
# 安装依赖
pip install pyyaml

# 一键安装/更新补全（扫描 + 生成 + 安装到 shell 配置）
bash install.sh

# 单独运行各阶段（调试用）
python cc_scan.py        # 阶段一：扫描命令树，生成 data/claude.yaml
python cc_generate.py    # 阶段二：读取 YAML，生成补全脚本

# 语法验证
zsh -n completions/_claude
bash -n completions/claude.bash
```

## 架构

Pipeline 分两个独立阶段，中间以 `data/claude.yaml` 解耦：

**`cc_scan.py`（扫描器）**
- `run_help(cmd_path)` → 执行 `claude [subcmds...] --help`，超时 5 秒
- `parse_options(text)` / `parse_commands(text)` → 用正则解析 help 输出的 Options/Commands section
- `scan_node(cmd_path, visited)` → 递归构建命令树节点，`visited` set 防止循环
- 输出：`data/claude.yaml`，结构为嵌套的 `{name, description, options, commands}` 节点

**`cc_generate.py`（生成器）**
- zsh 路径：`generate_zsh()` 为每个命令节点递归生成独立补全函数（`_claude`、`_claude_auth` 等），使用 `_arguments -C` + `case $state` 模式
- bash 路径：`_collect_bash_cases()` 将命令树展平为 `case_key → completions` 列表，`build_bash_script()` 生成单一函数 + `case "$cmd"` 分发
- 输出：`completions/_claude`（zsh）和 `completions/claude.bash`（bash）

**`install.sh`（安装器）**
- 检测当前交互式 shell（通过父进程 `ps -p $PPID`，而非 `$SHELL` 环境变量）
- 自动依次执行 `cc_scan.py` → `cc_generate.py`，再将补全脚本安装到对应位置
- zsh：复制到 `~/.zsh/completions/`，并向 `~/.zshrc` 写入 `fpath` 和 `compinit` 配置
- bash：向 `~/.bashrc` 追加 `source` 行；已存在则跳过

**关键设计决策**
- zsh 函数命名：`_` + 路径各级用 `_` 连接，如 `_claude_auth_login`
- bash 补全通过扫描 `COMP_WORDS` 找到第一个非选项词作为子命令 key，再用 `compgen -W` 生成候选
- `data/claude.yaml` 可手动编辑后单独运行 `cc_generate.py` 更新补全脚本，无需重新扫描
