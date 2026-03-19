# Claude Code CLI 补全工具

为 `claude` CLI 自动生成 zsh 和 bash 的 Tab 补全脚本。

## 功能

- 自动递归扫描 `claude` 命令树，覆盖所有子命令和选项
- 同时支持 **zsh** 和 **bash** 两种 shell
- 一键安装，自动写入 shell 配置文件
- 中间产物 `data/claude.yaml` 可手动编辑，无需重新扫描即可重新生成脚本

## 环境要求

- Python 3.9+
- [pyyaml](https://pypi.org/project/PyYAML/)：`pip install pyyaml`
- 已安装 [Claude Code CLI](https://github.com/anthropics/claude-code)（`claude` 命令可用）

## 安装

```bash
bash install.sh
```

脚本会自动完成以下步骤：

1. 扫描 `claude` 命令树，生成 `data/claude.yaml`
2. 根据当前 shell 生成对应的补全脚本
3. 将补全脚本安装到正确位置，并更新 shell 配置文件

安装完成后按提示执行 `source ~/.zshrc`（或 `~/.bashrc`）即可立即生效。

## 更新补全

当 `claude` 更新、添加了新命令时，重新运行安装脚本即可：

```bash
bash install.sh
```

也可以手动编辑 `data/claude.yaml`（添加自定义描述、补充缺失选项等），然后单独运行生成器更新脚本而无需重新扫描：

```bash
python cc_generate.py
```

## 项目结构

```
├── install.sh           # 一键安装脚本
├── cc_scan.py           # 扫描器：递归调用 claude --help，输出 YAML
├── cc_generate.py       # 生成器：读取 YAML，生成 shell 补全脚本
├── data/
│   └── claude.yaml      # 命令树数据（中间层，可手动编辑）
└── completions/
    ├── _claude          # zsh 补全脚本
    └── claude.bash      # bash 补全脚本
```

## 注意事项

- 安装脚本通过检测**父进程**判断当前 shell，因此无论以 `bash install.sh` 还是 `sh install.sh` 运行，都能正确识别终端所用的 shell
- 若 `~/.zshrc` 中已存在 `fpath` 或 `compinit` 配置，安装脚本会自动跳过，不会重复写入
- `data/claude.yaml` 是解耦中间层，可在不重新扫描的情况下单独编辑后重新生成补全脚本

## License

Copyright 2026 chenhang

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
