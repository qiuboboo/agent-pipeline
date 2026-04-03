# 新服务器从 0 到可跑结果：Ubuntu 操作步骤

本文档面向 **全新 Ubuntu 服务器**，目标是把 `agent-pipeline` 从零部署到可运行，并能使用当前接通的 **responses API** 跑出结果。

---

## 1. 目标

部署完成后，你应当能够：

- clone 当前分支代码
- 安装 Python 依赖
- 配置新的 API
- 运行单数据集 / 多数据集 YAML
- 运行带手动范围参数的 EEE-Bench 批跑脚本
- 在 Ubuntu 下查看任务状态、日志、进程、结果目录

---

## 2. 环境假设

建议系统：

- Ubuntu 22.04 / 24.04
- Python 3.10+
- git 已安装
- 能访问 Hugging Face / GitHub / 你的 API 网关

建议用户目录示例：

```bash
/home/ubuntu/work
```

本文默认项目部署在：

```bash
/home/ubuntu/work/agent-pipeline
```

---

## 3. 安装基础环境

### 3.1 系统依赖

```bash
sudo apt update
sudo apt install -y git curl wget python3 python3-venv python3-pip build-essential
```

### 3.2 创建工作目录

```bash
mkdir -p ~/work
cd ~/work
```

---

## 4. 拉取代码

### 4.1 clone 仓库

```bash
git clone <YOUR_REPO_URL>
cd agent-pipeline
```

### 4.2 切到目标分支

```bash
git checkout ler-reasoning-chain-msearth
```

### 4.3 确认你拉到的是最新提交

```bash
git log --oneline -n 5
```

---

## 5. 创建 Python 环境

### 5.1 创建虚拟环境

```bash
python3 -m venv .venv
```

### 5.2 激活虚拟环境

```bash
source .venv/bin/activate
```

激活后终端前面通常会出现：

```bash
(.venv)
```

### 5.3 安装依赖

如果仓库里有 `requirements.txt`：

```bash
pip install -U pip
pip install -r requirements.txt
```

如果项目使用别的依赖管理方式，就按项目实际文件安装。

---

## 6. 配置环境变量

当前这套可用 API：

- `base_url = https://cf.cuylerchen.uk/openai/v1`
- `api_mode = responses`
- `api_key = 你的 cr_...`

### 6.1 临时导出（当前 shell 生效）

```bash
export CUSTOM_OPENAI_API_KEY="YOUR_CR_KEY"
export CUSTOM_OPENAI_BASE_URL="https://cf.cuylerchen.uk/openai/v1"
export CUSTOM_OPENAI_API_MODE="responses"
```

### 6.2 写入 `~/.bashrc`（新 shell 也生效）

```bash
echo 'export CUSTOM_OPENAI_API_KEY="YOUR_CR_KEY"' >> ~/.bashrc
echo 'export CUSTOM_OPENAI_BASE_URL="https://cf.cuylerchen.uk/openai/v1"' >> ~/.bashrc
echo 'export CUSTOM_OPENAI_API_MODE="responses"' >> ~/.bashrc
source ~/.bashrc
```

### 6.3 可选：Hugging Face token

如果你后面下载数据经常慢，建议加：

```bash
export HF_TOKEN="YOUR_HF_TOKEN"
```

并写进 `~/.bashrc`。

---

## 7. 先做最小验证

### 7.1 EEE-Bench 1 条 smoke

```bash
python3 scripts/eee_bench_batch_launcher.py \
  --start 300 \
  --end 301 \
  --step 20 \
  --base-url "$CUSTOM_OPENAI_BASE_URL" \
  --api-key "$CUSTOM_OPENAI_API_KEY" \
  --api-mode responses
```

### 7.2 单数据集 YAML 验证（示例：MM-Math）

```bash
python3 run_pipeline.py \
  --config configs/mm_math_validation_10.responses.yaml \
  --api-key "$CUSTOM_OPENAI_API_KEY"
```

---

## 8. 当前可用 YAML 配置

当前建议保留并可直接跑的配置包括：

### 单数据集
- `configs/mm_math_validation_10.responses.yaml`
- `configs/multi_physics_validation_10.responses.yaml`
- `configs/seephys_validation_10.responses.yaml`
- `configs/emma_physics_validation_3.responses.yaml`
- `configs/emma_physics_validation_1.responses.yaml`

### 多数据集
- `configs/three_datasets_validation_3.responses.yaml`

---

## 9. 新增：四个数据集总配置

如果你要一起验证四个数据集：

- `MM-Math`
- `Multi-Physics`
- `SeePhys`
- `EMMA-Physics`

请使用：

- `configs/four_datasets_responses_10.yaml`

运行方式：

```bash
python3 run_pipeline.py \
  --config configs/four_datasets_responses_10.yaml \
  --api-key "$CUSTOM_OPENAI_API_KEY"
```

---

## 10. 运行脚本：手动输入 EEE-Bench 范围

已提供脚本：

- `scripts/run_eee_bench_range.sh`

用法：

```bash
bash scripts/run_eee_bench_range.sh 320 500 20
```

含义：

- 起点：`320`
- 终点：`500`
- 步长：`20`

脚本会自动：

- 检查环境变量
- 创建日志目录
- 使用 responses API 跑 EEE-Bench
- 输出日志路径

---

## 11. Ubuntu 下怎么看任务是否在跑

### 11.1 查看 Python 进程

```bash
ps -ef | grep python | grep -v grep
```

### 11.2 查看特定任务

#### 看 EEE-Bench

```bash
ps -ef | grep eee_bench | grep -v grep
```

#### 看 run_pipeline

```bash
ps -ef | grep run_pipeline.py | grep -v grep
```

### 11.3 实时看日志

```bash
tail -f .runlogs/eee_bench_responses.log
```

或：

```bash
tail -f outputs/<your_run_dir>/summary.json
```

### 11.4 查看最近 100 行日志

```bash
tail -n 100 .runlogs/eee_bench_responses.log
```

---

## 12. Ubuntu 下怎么看结果是否跑完

### 12.1 看 summary.json

```bash
cat outputs/<run_dir>/summary.json
```

你重点看这些字段：

- `processed_samples`
- `decision_counts`
- `llm_usage.successful_request_count`
- `llm_usage.failed_request_count`
- `llm_usage.last_error`

### 12.2 看每个数据集自己的 summary

```bash
find outputs/<run_dir>/datasets -name summary.json -print
```

### 12.3 看样本文件

```bash
find outputs/<run_dir>/datasets -path "*/samples/*.json"
```

---

## 13. Ubuntu 下怎么停任务

### 13.1 按名字停

```bash
pkill -f run_pipeline.py
```

或者：

```bash
pkill -f eee_bench_batch_launcher.py
```

### 13.2 先查 PID 再 kill

```bash
ps -ef | grep run_pipeline.py | grep -v grep
kill <PID>
```

如果普通 `kill` 不行，再用：

```bash
kill -9 <PID>
```

---

## 14. 推荐后台运行方式

### 14.1 用 nohup

```bash
nohup python3 run_pipeline.py \
  --config configs/mm_math_validation_10.responses.yaml \
  --api-key "$CUSTOM_OPENAI_API_KEY" \
  > .runlogs/mm_math_validation_10.log 2>&1 &
```

### 14.2 查看后台 PID

```bash
echo $!
```

### 14.3 持续看日志

```bash
tail -f .runlogs/mm_math_validation_10.log
```

---

## 15. 常见问题排查

### 问题 1：`Route /chat/completions not found`
原因：
- 你用了旧接口模式

解决：
- 确保 base_url 是：
  `https://cf.cuylerchen.uk/openai/v1`
- 确保配置里：
  `api_mode: responses`

### 问题 2：Hugging Face 下载太慢 / 失败
解决：
- 配 `HF_TOKEN`
- 多试几次
- 确认服务器能访问 huggingface.co

### 问题 3：任务跑了但结果全坏
先看：

```bash
cat outputs/<run_dir>/summary.json
```

重点关注：
- `failed_request_count`
- `last_error`

### 问题 4：YAML 改了但运行结果没变
原因：
- 旧任务已经启动，启动时就已经读了旧配置

解决：
- 停掉旧任务
- 重启新任务

---

## 16. 建议部署顺序

推荐第一次上新服务器时按这个顺序：

1. clone 代码
2. 建 venv + 安装依赖
3. 配环境变量
4. 跑 1 条 smoke
5. 跑单数据集 3 / 10 条验证
6. 确认稳定后再跑长任务

---

## 17. 这套里我建议优先级

### 当前表现最好
- `SeePhys`

### 可用但 review 偏多
- `MM-Math`
- `Multi-Physics`
- `EMMA-Physics`

如果新服务器第一次上线，建议优先先跑：

1. `SeePhys`
2. `MM-Math`
3. 再跑其他

---

## 18. 一组可直接复制的最小命令

```bash
cd ~/work
git clone <YOUR_REPO_URL>
cd agent-pipeline
git checkout ler-reasoning-chain-msearth
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

export CUSTOM_OPENAI_API_KEY="YOUR_CR_KEY"
export CUSTOM_OPENAI_BASE_URL="https://cf.cuylerchen.uk/openai/v1"
export CUSTOM_OPENAI_API_MODE="responses"

python3 run_pipeline.py \
  --config configs/seephys_validation_10.responses.yaml \
  --api-key "$CUSTOM_OPENAI_API_KEY"
```

---

## 19. 最后建议

新机第一次跑，不要直接大跑。

最稳顺序：

- smoke
- 3 条
- 10 条
- 长任务

这样能最快定位问题，也最不容易一口气浪费大量样本与 API 调用。
