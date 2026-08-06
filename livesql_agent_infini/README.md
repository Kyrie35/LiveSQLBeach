# LiveSQLBench × InfiniSynapse Agent

在 LiveSQLBench Base-Lite-SQLite 上复用 InfiniSynapse 刷题能力，代码独立于 Spider2 项目。

## Step 1: 注册数据库

### 1. 安装依赖

```bash
cd livesql_agent_infini
pip install -e .
```

### 2. 配置 InfiniSynapse 凭证

将 Spider2 项目里已验证可用的凭证复制过来：

```bash
cp /path/to/spider_agent_infini/infini_credential.json ./infini_credential.json
```

或参考 `infini_credential.json.example` 自行填写。

### 3. 预览将要注册的数据库

```bash
python setup_livesql.py --dry-run
```

应发现 18 个库（`alien`, `archeology`, ..., `virtual`）。

### 4. 注册全部 SQLite 数据库

```bash
python setup_livesql.py
```

只注册单个库：

```bash
python setup_livesql.py --db alien
```

若已存在且需要重建：

```bash
python setup_livesql.py --db alien --force
```

### 5. 验证注册结果

```bash
python3 setup_livesql.py --verify
python3 setup_livesql.py --list-remote
```

如果连接远程 InfiniSynapse（如 `dev-app.infinisynapse.com`）较慢，可加大超时：

```bash
python3 setup_livesql.py --db alien --verify --timeout 90
# 或
export INFINI_API_TIMEOUT=90
python3 setup_livesql.py --list-remote
```

## 命名规则

为避免与 Spider2 已注册的 SQLite 数据源冲突，LiveSQLBench 库在 InfiniSynapse 中的名称统一为：

```text
livesql_{selected_database}
```

例如 `alien` → `livesql_alien`，`cross_db` → `livesql_cross_db`。

后续 `run_livesql.py` 会通过 `selected_database` 字段查找对应数据源。

## 目录结构

```text
livesql_agent_infini/
├── setup_livesql.py              # CLI 入口
├── infini_credential.json        # 本地凭证（勿提交）
├── livesql_agent_infini/
│   ├── config.py                 # 路径与命名前缀
│   ├── setup_livesql.py          # 注册逻辑
│   └── api/                      # InfiniSynapse API 封装
└── setup_failures.log            # 注册失败日志（运行后生成）
```

数据集默认路径：`../livesqlbench-base-lite-sqlite/`

## Step 2: 跑第一题（Query）

当前只注册了 `livesql_alien` 时，先跑 alien 库的第一题：

```bash
python3 run_livesql.py \
  --instance_id alien_1 \
  --timeout 90
```

常用参数（对齐 Spider 的 `run.py` 习惯）：

| 参数 | 作用 |
|------|------|
| `--instance_id alien_1` | 只跑指定题 |
| `--db_id alien` | 只跑某个库下的 Query 题 |
| `--engine <name>` | 指定 InfiniSQL 引擎 |
| `--rerun` | 强制重跑并覆盖已有提交 |

重跑单题时，`submission_output.jsonl` **只更新该题对应行**，不会删除其他题的记录。

```bash
python3 run_livesql.py --instance_id alien_1 --rerun --timeout 90
```
| `--timeout 90` | API 超时（秒） |

产物位置：

```text
submission_sql/alien_1.sql          # Agent 产出的 SQL
submission_reasoning/alien_1.json   # reasoning trace
submission_output.jsonl             # 含 pred_sqls，供后续评测
output/alien_1/                     # task workspace 压缩包
references/alien_1_kb.md            # 按 external_knowledge 生成的参考文档
```

跑完后本地评测（终端会列出 PASSED / FAILED 的 instance_id）：

```bash
python3 ../live_sql_bench_sqlite/evaluation/wrapper_evaluation_sqlite.py \
  --jsonl_file submission_output.jsonl \
  --db_path ../livesqlbench-base-lite-sqlite \
  --mode pred \
  --num_threads 1
```
