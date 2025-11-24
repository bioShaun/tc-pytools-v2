# TC PyTools

基因组数据处理工具集。

## 项目概述

本项目使用 [uv](https://github.com/astral-sh/uv) 进行包管理和依赖管理，包含多个用于基因组数据处理的工具。

## 安装

```bash
# 克隆或进入项目目录
cd tc-pytools-v1.1

# 安装依赖
uv sync
```

## 工具列表

### 1. rename-ngdc-genome-id

重命名 NGDC 基因组 FASTA 和 GFF 文件中的染色体 ID。

**快速使用**：
```bash
uv run rename-ngdc-genome-id -f genome.fasta -o output.fasta
```

**详细文档**: [gtf/docs/README.md](gtf/docs/README.md)

## 开发

### 快速命令

```bash
make help          # 查看所有可用命令
make test          # 运行测试
make ci            # 运行完整 CI 检查
./ci.sh            # 运行本地 CI 脚本
```

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行测试并生成覆盖率报告
uv run pytest --cov

# 查看 HTML 覆盖率报告
uv run pytest --cov --cov-report=html
# 打开 htmlcov/index.html
```

### 代码质量

```bash
# 代码格式化
make format

# 代码检查
make lint

# 类型检查
make type-check
```

### 本地 CI

项目提供三种本地 CI 方式：

1. **CI 脚本**: `./ci.sh`
2. **Make 命令**: `make ci`
3. **Pre-commit**: `uv run pre-commit run --all-files`

详细使用说明请参考 [QUICKREF.md](QUICKREF.md)

## 项目结构

```
tc-pytools-v1.1/
├── gtf/                    # GTF 相关工具
│   ├── rename_ngdc_genome_id.py
│   ├── docs/              # 工具文档
│   └── tests/             # 单元测试
├── pyproject.toml         # 项目配置
├── Makefile              # Make 命令
├── ci.sh                 # CI 脚本
└── QUICKREF.md           # 快速参考
```

## 文档

- [QUICKREF.md](QUICKREF.md) - 快速参考指南（中文）
- [SETUP_COMPLETE.md](SETUP_COMPLETE.md) - 项目配置说明
- 各工具的详细文档位于对应的 `docs/` 目录下

## 许可证

MIT
