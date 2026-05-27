# KnowledgeVault — 基于 RAG 的智能知识检索与隐私保护分析系统

一个基于 **RAG（检索增强生成）** 架构的本地知识库问答系统。上传你的文档，系统自动分块、索引，然后用 LLM 生成带引用来源的专业分析报告。

**特点**：本地运行、知识库可扩充、敏感信息自动脱敏、Prompt 全链路可视化。

## 你能用它做什么

- **上传文档即用**：拖拽 `.txt` 文件到知识库，自动完成分词、向量化、索引
- **自然语言提问**：输入问题，系统从知识库中检索相关内容，结合 LLM 生成分析报告
- **隐私保护**：报告发送到云端 API 前，自动隐藏手机号、身份证号、银行卡号、邮箱、姓名、表格数据
- **Prompt 可视化**：在 Web 界面查看完整的 System Prompt 和 User Prompt，看清上下文是如何组装的
- **一键评估**：自动评估抽取质量和生成质量，量化验证 RAG 管道效果

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
# 从模板创建 .env 文件
cp .env.example .env

# 编辑 .env，填入你的 DeepSeek API Key
# DEEPSEEK_API_KEY = "sk-xxxxxxxx"
```

密钥存储在 `.env` 文件中，已加入 `.gitignore`，不会被提交到 Git。

### 3. 启动服务

```bash
# 启动 Web 服务（推荐）
python server.py

# 浏览器打开 http://localhost:8765
```

首次启动会自动下载 Embedding 模型（约 100MB），之后即可直接使用。

### 命令行模式

```bash
# 运行完整管道（一次性批处理）
python main.py

# 跳过 LLM 调用，仅测试本地模块
python main.py --skip-extraction --skip-generation

# 追加自定义查询
python main.py -q "分析这三家公司的盈利能力对比"
```

## 项目结构

```
.
├── server.py                   # Web 服务入口（FastAPI + REST API）
├── main.py                     # 命令行管道编排器
├── config.py                   # 所有可配置参数集中管理
├── requirements.txt            # 依赖清单
│
├── frontend/
│   └── index.html              # Vue3 单页应用（CDN 引入，无需构建）
│
├── modules/
│   ├── data_loader.py          # 读取 .txt 文档
│   ├── chunker.py              # 段落感知分块（重叠策略）
│   ├── extractor.py            # LLM 信息抽取 → 结构化字段
│   ├── embedder.py             # 本地 Embedding → ChromaDB
│   ├── retriever.py            # 查询向量化 + Top-K 语义检索
│   ├── generator.py            # RAG 报告生成（含隐私脱敏）
│   ├── evaluator.py            # 抽取/检索/生成质量评估
│   └── privacy.py              # 敏感信息检测与脱敏
│
├── prompts/
│   ├── extraction.py           # 抽取 Prompt 模板
│   └── generation.py           # 报告生成 Prompt 模板
│
├── db/
│   ├── schema.py               # 5 张表的建表语句
│   └── repository.py           # 数据库读写操作
│
├── data/
│   ├── sample_docs/            # 知识库文档存放目录（.txt）
│   └── ground_truth.json       # 人工标注真值（评估用）
│
├── utils/
│   └── helpers.py              # 日志、计时、JSON 安全解析等工具函数
│
├── chroma_store/               # ChromaDB 持久化目录（运行后自动生成）
└── output/                     # 生成的 Markdown 报告（运行后自动生成）
```

## 技术架构

```
上传 .txt → 段落分块 → LLM 抽取字段 → SQLite 存储
                    ↘
              本地 Embedding → ChromaDB 向量索引

用户提问 → 向量检索 → 拼接 Prompt → LLM 生成报告 → Markdown 输出
                          ↑
                    PII 自动脱敏
```

| 组件 | 选型 | 说明 |
|------|------|------|
| 大模型 | DeepSeek Chat | 负责抽取和生成 |
| Embedding | BAAI/bge-small-zh-v1.5 | 本地运行，无 API 调用 |
| 向量数据库 | ChromaDB | 持久化存储，重启不丢失 |
| 结构化存储 | SQLite | 5 张表，文件级数据库 |
| 前端 | Vue3 + marked.js | CDN 引入，零构建步骤 |
| 后端 | FastAPI + uvicorn | 异步支持，自动生成 API 文档 |

> 不使用 LangChain 等重量级框架，所有代码纯 Python 实现，逻辑清晰可读。

## Web 界面指南

打开 `http://localhost:8765` 后你会看到：

- **顶部状态栏**：管道就绪状态、API Key 配置状态、向量索引数量
- **隐私保护横幅**：说明数据脱敏策略
- **知识库管理**（可折叠）：查看已上传文档、拖拽上传新 `.txt` 文件、删除文档
- **搜索框**：输入问题，支持快捷示例一键填入
- **分析报告 Tab**：Markdown 渲染的五段式财务分析报告
- **Prompt 工程 Tab**：查看 System Prompt 和 User Prompt，颜色标注上下文注入位置
- **检索结果 Tab**：展示检索到的文档片段及相关度分数

### 知识库管理

- **上传**：点击或拖拽 `.txt` 文件到上传区域，系统自动完成分块、Embedding、入库
- **查看**：知识库面板列出所有文档，包含分块数和字数统计
- **删除**：每个文档旁有删除按钮，确认后从数据库、向量库和磁盘一并清除

## API 接口

所有接口均在 `http://localhost:8765` 下：

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | Web 交互界面 |
| `GET` | `/api/health` | 系统健康检查 |
| `POST` | `/api/query` | 提交查询，返回检索结果 + AI 报告 |
| `POST` | `/api/extract` | 触发 LLM 信息抽取 |
| `GET` | `/api/knowledge` | 查看知识库文档列表 |
| `POST` | `/api/knowledge/upload` | 上传 .txt 文件到知识库 |
| `DELETE` | `/api/knowledge/{doc_id}` | 删除指定文档 |

查询请求示例：

```bash
curl -X POST http://localhost:8765/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "深圳创新科技2024年的财务状况如何？", "top_k": 5}'
```

上传文件示例：

```bash
curl -X POST http://localhost:8765/api/knowledge/upload \
  -F "files=@我的文档.txt"
```

## 隐私保护机制

系统在将检索到的文本发送给 DeepSeek API 之前，**自动检测并替换**以下敏感信息：

| 类型 | 检测方式 | 替换为 |
|------|---------|--------|
| 手机号 | `1[3-9]\d{9}` 精确匹配 | `[手机号已隐藏]` |
| 身份证号 | 18 位数字 + 校验位 | `[身份证号已隐藏]` |
| 银行卡号 | 16-19 位连续数字 | `[银行卡号已隐藏]` |
| 电子邮箱 | 标准邮箱正则 | `[邮箱已隐藏]` |
| 人员姓名 | "姓名/联系人/法定代表人" 等模式 | `[姓名已隐藏]` |
| 表格数据 | Markdown 表格 / TSV 行 | `[表格行已隐藏]` |

脱敏后的 Prompt 可在 Web 界面的「Prompt 工程」标签页查看验证。API 返回的 `pii_redacted` 字段会告知本次脱敏数量。

## 数据库设计

5 张表，关系清晰：

```
documents ──1:N──> chunks ──1:N──> extracted_entities
                      │
                      └──> analysis_reports（通过 retrieved_chunk_ids JSON 关联）

evaluation_results ──> 独立记录，通过 reference_id 关联报告或抽取
```

| 表名 | 存储内容 |
|------|---------|
| `documents` | 文档文件名、标题、来源路径 |
| `chunks` | 文档分块内容、分块序号、字符数 |
| `extracted_entities` | 从分块中抽取的公司名、营收、净利润、增长率等 15+ 字段 |
| `analysis_reports` | 用户查询、检索到的分块 ID、生成的报告正文、耗时 |
| `evaluation_results` | 评估指标名称和数值（精确率、召回率、完整性等） |

## Prompt 工程

系统通过精心设计的 Prompt 控制 LLM 输出质量：

**抽取阶段**：角色设定为「中文财务数据抽取专家」，内联 Schema 定义 15 个字段，硬约束（不推测、缺失设 null），Few-shot 示例引导，末尾强约束「仅返回 JSON」。

**生成阶段**：角色设定为「资深金融分析师」，五段式 Markdown 报告模板（摘要 → 财务分析 → 事件 → 风险 → 展望），要求标注数据来源，区分确定事实与推断结论。

Web 界面中可查看每次查询组装的完整 System Prompt 和 User Prompt，检索上下文和结构化数据分别用颜色标注。

## 评估体系

| 阶段 | 指标数 | 核心指标 |
|------|--------|---------|
| 信息抽取 | 10 项 | 公司名模糊匹配、营收/净利润数值精度、日期精确匹配、关键人物 Jaccard、JSON 有效率 |
| 语义检索 | 3 项 | Precision@k、Recall@k、F1@k |
| 报告生成 | 4 项 | 章节完整性、数据引用数、长度合理性、幻觉检测 |

## 可配置参数

在 `config.py` 中集中管理，支持通过 `.env` 覆盖密钥：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `CHUNK_MAX_CHARS` | 1000 | 分块最大字符数 |
| `CHUNK_OVERLAP_CHARS` | 200 | 相邻块重叠字符数 |
| `TOP_K_RETRIEVAL` | 5 | 每次检索返回的片段数 |
| `EXTRACTION_TEMPERATURE` | 0.1 | 抽取时的 LLM 温度 |
| `GENERATION_TEMPERATURE` | 0.3 | 生成报告时的 LLM 温度 |

## 许可证

MIT License
