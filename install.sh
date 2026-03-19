#!/usr/bin/env sh
# install.sh — 自动检测 shell 环境并安装 claude 补全脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ZSH_COMPLETION="$SCRIPT_DIR/completions/_claude"
BASH_COMPLETION="$SCRIPT_DIR/completions/claude.bash"

# ── 颜色支持（检测终端）────────────────────────────────────────────
if [ -t 1 ] && [ "${NO_COLOR:-}" = "" ]; then
    BOLD="$(printf '\033[1m')";  DIM="$(printf '\033[2m')"
    RED="$(printf '\033[31m')";  GREEN="$(printf '\033[32m')"
    YELLOW="$(printf '\033[33m')"; CYAN="$(printf '\033[36m')"
    RESET="$(printf '\033[0m')"
else
    BOLD=""; DIM=""; RED=""; GREEN=""; YELLOW=""; CYAN=""; RESET=""
fi

info()    { printf "  ${DIM}ℹ${RESET}  %s\n" "$1"; }
ok()      { printf "  ${GREEN}✅${RESET} %s\n" "$1"; }
warn()    { printf "  ${YELLOW}⚠️ ${RESET} %s\n" "$1"; }
err()     { printf "  ${RED}❌${RESET} ${BOLD}%s${RESET}\n" "$1"; }
cmd_hint(){ printf "  ${DIM}\$${RESET}  ${CYAN}%s${RESET}\n" "$1"; }

# ── 检查 claude 是否已安装 ────────────────────────────────────────
printf "\n${BOLD}🚀 安装 claude CLI 补全脚本${RESET}\n\n"

if command -v claude > /dev/null 2>&1; then
    info "检测到 claude 已安装，正在更新补全数据..."
    printf "\n"
    python "$SCRIPT_DIR/cc_scan.py" && python "$SCRIPT_DIR/cc_generate.py"
    printf "\n"
else
    err "未找到 claude 命令"
    info "请先安装 Claude Code CLI："
    cmd_hint "npm install -g @anthropic-ai/claude-code"
    printf "\n"
    exit 1
fi

# ── 检测当前 shell（查父进程，避免 sh/bash 运行脚本时误判）────────────
_PPID="$(ps -p $$ -o ppid= 2>/dev/null | tr -d ' ')"
CURRENT_SHELL="$(ps -p "$_PPID" -o comm= 2>/dev/null | sed 's/^-//')"
# 父进程也无法判断时，回退到 $SHELL
if [ -z "$CURRENT_SHELL" ]; then
    CURRENT_SHELL="$(basename "$SHELL")"
fi

install_zsh() {
    ZSH_COMP_DIR="$HOME/.zsh/completions"
    ZSHRC="$HOME/.zshrc"

    mkdir -p "$ZSH_COMP_DIR"
    cp "$ZSH_COMPLETION" "$ZSH_COMP_DIR/_claude"
    ok "补全脚本已复制到 ${BOLD}$ZSH_COMP_DIR/_claude${RESET}"

    # 添加 fpath（如未添加）
    if ! grep -qF 'fpath=(~/.zsh/completions' "$ZSHRC" 2>/dev/null; then
        printf '\n# claude CLI 补全\nfpath=(~/.zsh/completions $fpath)\n' >> "$ZSHRC"
        ok "已向 ${BOLD}$ZSHRC${RESET} 添加 fpath 配置"
    else
        warn "fpath 配置已存在，跳过"
    fi

    # 添加 compinit（如未添加）
    if ! grep -qF 'compinit' "$ZSHRC" 2>/dev/null; then
        printf 'autoload -U compinit && compinit\n' >> "$ZSHRC"
        ok "已向 ${BOLD}$ZSHRC${RESET} 添加 compinit"
    else
        warn "compinit 已存在，跳过"
    fi

    printf "\n${BOLD}🎉 安装完成！${RESET}运行以下命令立即生效：\n\n"
    cmd_hint "source $ZSHRC"
    printf "\n"
}

install_bash() {
    BASHRC="$HOME/.bashrc"
    SOURCE_LINE="source $BASH_COMPLETION"

    if grep -qF "$SOURCE_LINE" "$BASHRC" 2>/dev/null; then
        warn "bash 补全已安装，无需重复添加"
    else
        printf '\n# claude CLI 补全\n%s\n' "$SOURCE_LINE" >> "$BASHRC"
        ok "已向 ${BOLD}$BASHRC${RESET} 添加 source 配置"
    fi

    printf "\n${BOLD}🎉 安装完成！${RESET}运行以下命令立即生效：\n\n"
    cmd_hint "source $BASHRC"
    printf "\n"
}

case "$CURRENT_SHELL" in
    zsh)
        info "检测到 ${BOLD}zsh${RESET} 环境，开始安装补全..."
        printf "\n"
        install_zsh
        ;;
    bash)
        info "检测到 ${BOLD}bash${RESET} 环境，开始安装补全..."
        printf "\n"
        install_bash
        ;;
    *)
        err "未识别的 shell：$CURRENT_SHELL"
        info "请手动安装："
        printf "\n"
        printf "  ${CYAN}zsh${RESET}\n"
        cmd_hint "cp $ZSH_COMPLETION ~/.zsh/completions/_claude"
        printf "\n"
        printf "  ${CYAN}bash${RESET}\n"
        cmd_hint "echo 'source $BASH_COMPLETION' >> ~/.bashrc"
        printf "\n"
        exit 1
        ;;
esac
