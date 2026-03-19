# bash completion for claude
# 由 cc_generate.py 自动生成
# 用法：在 ~/.bashrc 中添加：source /path/to/claude.bash

_claude_completions() {
  local cur prev words cword
  _init_completion 2>/dev/null || {
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
  }

  # 找出当前使用的子命令
  local cmd=""
  local i
  for ((i=1; i < COMP_CWORD; i++)); do
    if [[ "${COMP_WORDS[i]}" != -* ]]; then
      cmd="${COMP_WORDS[i]}"
      break
    fi
  done

  case "$cmd" in
    agents)
      COMPREPLY=( $(compgen -W '-h --help --setting-sources' -- "$cur") )
      return 0
      ;;
    auth)
      COMPREPLY=( $(compgen -W '-h --help help login logout status' -- "$cur") )
      return 0
      ;;
    login)
      COMPREPLY=( $(compgen -W '--claudeai --console --email -h --help --sso' -- "$cur") )
      return 0
      ;;
    logout)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    status)
      COMPREPLY=( $(compgen -W '-h --help --json --text' -- "$cur") )
      return 0
      ;;
    doctor)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    install)
      COMPREPLY=( $(compgen -W '--force -h --help' -- "$cur") )
      return 0
      ;;
    mcp)
      COMPREPLY=( $(compgen -W '-h --help add' -- "$cur") )
      return 0
      ;;
    add)
      COMPREPLY=( $(compgen -W '--callback-port --client-id --client-secret -e --env -H --header -h --help -s --scope -t --transport' -- "$cur") )
      return 0
      ;;
    plugin)
      COMPREPLY=( $(compgen -W '-h --help disable enable help install i list marketplace uninstall remove update validate' -- "$cur") )
      return 0
      ;;
    disable)
      COMPREPLY=( $(compgen -W '-a --all -h --help -s --scope' -- "$cur") )
      return 0
      ;;
    enable)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    install)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    i)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    list)
      COMPREPLY=( $(compgen -W '--available -h --help --json' -- "$cur") )
      return 0
      ;;
    marketplace)
      COMPREPLY=( $(compgen -W '-h --help add help list remove rm update' -- "$cur") )
      return 0
      ;;
    add)
      COMPREPLY=( $(compgen -W '-h --help --scope --sparse' -- "$cur") )
      return 0
      ;;
    list)
      COMPREPLY=( $(compgen -W '-h --help --json' -- "$cur") )
      return 0
      ;;
    remove)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    rm)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    update)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    uninstall)
      COMPREPLY=( $(compgen -W '-h --help --keep-data -s --scope' -- "$cur") )
      return 0
      ;;
    remove)
      COMPREPLY=( $(compgen -W '-h --help --keep-data -s --scope' -- "$cur") )
      return 0
      ;;
    update)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    validate)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    plugins)
      COMPREPLY=( $(compgen -W '-h --help disable enable help install i list marketplace uninstall remove update validate' -- "$cur") )
      return 0
      ;;
    disable)
      COMPREPLY=( $(compgen -W '-a --all -h --help -s --scope' -- "$cur") )
      return 0
      ;;
    enable)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    install)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    i)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    list)
      COMPREPLY=( $(compgen -W '--available -h --help --json' -- "$cur") )
      return 0
      ;;
    marketplace)
      COMPREPLY=( $(compgen -W '-h --help add help list remove rm update' -- "$cur") )
      return 0
      ;;
    add)
      COMPREPLY=( $(compgen -W '-h --help --scope --sparse' -- "$cur") )
      return 0
      ;;
    list)
      COMPREPLY=( $(compgen -W '-h --help --json' -- "$cur") )
      return 0
      ;;
    remove)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    rm)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    update)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    uninstall)
      COMPREPLY=( $(compgen -W '-h --help --keep-data -s --scope' -- "$cur") )
      return 0
      ;;
    remove)
      COMPREPLY=( $(compgen -W '-h --help --keep-data -s --scope' -- "$cur") )
      return 0
      ;;
    update)
      COMPREPLY=( $(compgen -W '-h --help -s --scope' -- "$cur") )
      return 0
      ;;
    validate)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    setup-token)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    update)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    upgrade)
      COMPREPLY=( $(compgen -W '-h --help' -- "$cur") )
      return 0
      ;;
    *)
      COMPREPLY=( $(compgen -W '--add-dir --agent --agents --allow-dangerously-skip-permissions --allowedTools --allowed-tools --append-system-prompt --betas --brief --chrome -c --continue --dangerously-skip-permissions -d --debug --debug-file --disable-slash-commands --disallowedTools --disallowed-tools --effort --fallback-model --file --fork-session --from-pr -h --help --ide --include-partial-messages --input-format --json-schema --max-budget-usd --mcp-config --mcp-debug --model -n --name --no-chrome --no-session-persistence --output-format --permission-mode --plugin-dir -p --print --replay-user-messages -r --resume --session-id --setting-sources --settings --strict-mcp-config --system-prompt --tmux --tools --verbose -v --version -w --worktree agents auth doctor install mcp plugin plugins setup-token update upgrade' -- "$cur") )
      return 0
      ;;
  esac
}

complete -F _claude_completions claude
