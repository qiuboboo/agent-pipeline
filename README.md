# agent-pipeline

当前仓库已经完成一轮主线整理：
- 旧的 qjb / 剑波模块化实现相关内容已归档到 `archive/`
- 当前活跃代码与配置以 `ler` / `ler-reasoning-chain-msearth` 体系为主
- `ready/`、`plans/`、`docs/` 已重新整理为顶层主线目录

当前重点不再是继续扩展旧的模块化拆分，而是围绕现有 `src/benchmarkallinone/` 结构，稳定配置、输出与 ready 数据组织方式。

## 当前目录结构

```text
agent-pipeline/
├── archive/                    # 归档区，保存 qjb/main 旧结构与迁移前快照
├── configs/                    # 当前活跃 YAML 配置
├── docs/                       # 当前活跃文档与整理记录
├── outputs/                    # 当前活跃运行输出
├── plans/                      # 顶层计划文档
├── prompts/                    # 当前活跃 prompts
├── ready/                      # ready 数据集包（按“数据集+范围”命名）
├── scripts/                    # 当前活跃脚本
├── src/benchmarkallinone/      # 当前活跃代码
├── requirements.txt
└── run_pipeline.py             # 当前统一运行入口
```

## 目录职责

### `src/benchmarkallinone/`
当前活跃主代码目录。

入口 [run_pipeline.py](run_pipeline.py) 会把 `src/` 加入 `sys.path`，并从 `benchmarkallinone.pipeline` 导入主流程。

### `configs/`
当前活跃配置目录，主要来源于 `ler-reasoning-chain-msearth`，并参考 `ler` 补齐。

当前配置中的输出路径已统一指向：
- `outputs/...`

### `outputs/`
当前活跃运行输出目录。

旧的 `output/` 已不再作为主线目录，迁移前内容保留在归档中。

### `ready/`
当前 ready 数据集目录。

命名规则统一为：
- `数据集名字_起始_结束`

当前保留的代表性目录包括：
- `eee_bench_000_300`
- `geometry3k_000_100`
- `mathvision_000_020`
- `physreason_000_300`
- `phyx_000_500`
- `scemqa_000_100`
- `sciverse_000_500`

其中：
- `eee_bench_000_300` 与 `physreason_000_300` 已优先采用 `ler-reasoning-chain-msearth` 上游已合并好的 ready 结果
- `mathvision` 当前本地保留为 `000_020`
- `msearth_open_ended` 当前本地保留为 `000_002`，未直接切换到上游合并包，因为上游包不含图片资产

### `plans/`
当前顶层计划文档目录。

该目录已合并：
- 原 `docs/plans/`
- `ler/plans/`
- `ler-reasoning-chain-msearth/plans/`

### `docs/`
当前活跃文档目录。

保留内容包括：
- 当前整理记录
- dataset 验证/汇总文档
- branch 对比文档
- [pipeline初步设计.md](docs/pipeline初步设计.md)

原 main 中旧的 `architecture / contracts / migration / run_summaries` 已移入归档区。

### `archive/`
归档区，当前最重要的是：
- [archive/qjb_main_legacy/](archive/qjb_main_legacy/)

这里保存了：
- qjb / 剑波模块化实现相关根目录内容
- 旧 `benchmark/`
- 旧 docs 树
- 切换到 ler 主线前的 README / configs / scripts / src / output / ready 迁移备份

## 当前活跃文档

建议优先查看：

- [docs/2026-04-04_仓库整理记录.md](docs/2026-04-04_仓库整理记录.md)
- [docs/pipeline初步设计.md](docs/pipeline初步设计.md)
- [docs/qjb_ler_branch_report_2026-04-02.md](docs/qjb_ler_branch_report_2026-04-02.md)
- [docs/ler_reasoning_chain_msearth_detailed_report_2026-04-02.md](docs/ler_reasoning_chain_msearth_detailed_report_2026-04-02.md)

## 运行方式

### 1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

### 2. 运行默认配置

```bash
python run_pipeline.py --config configs/default_multidataset.yaml
```

### 3. 运行本地文件示例

```bash
python run_pipeline.py --config configs/local_file_example.yaml
```

## 当前状态说明

当前仓库已经完成第一轮结构整理，但还没有 commit。

目前已经确认：
- 入口已经切换到 `src/benchmarkallinone/`
- `configs/` 已切到 ler 体系
- `docs/`、`plans/`、`ready/` 已做第一轮收敛

目前仍需注意：
- 本地运行环境需补齐依赖，例如 `numpy`
- `ready/` 虽已按新规则完成第一轮重命名，但仍建议后续继续抽查每个目录的 `summary.json` 与 run 内容
- 当前仓库还处于整理后的未提交状态

## 本轮整理保留原则

- `docs/pipeline初步设计.md` 保留在活跃 `docs/`
- qjb / 剑波模块化实现不删除，统一归档
- `ready/` 统一改为“数据集名字 + 范围”命名
- 活跃主线优先采用 `ler-reasoning-chain-msearth` 的代码与文档状态# pipeline2
