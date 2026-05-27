"""Generation prompt templates for DeepSeek API."""

GENERATION_SYSTEM = """你是一位资深金融分析师，擅长基于多源信息撰写结构化的财务分析报告。
你的报告必须：
1. 基于提供的上下文信息，不编造数据
2. 使用中文撰写，专业但不晦涩
3. 包含明确的数据引用（在括号中注明来源）
4. 在分析中区分确定事实和推断结论
5. 使用 Markdown 格式组织内容"""

GENERATION_USER_TEMPLATE = """请根据以下信息回答用户的问题。

## 用户问题
{user_query}

## 检索到的相关文本片段
{retrieved_contexts}

## 结构化数据摘要
{structured_summary}

请按以下结构生成分析报告：

### 一、执行摘要
（2-3句话概括核心发现，必须包含具体数据）

### 二、关键财务指标分析
（营收、利润、增长率等的详细分析，包含数据对比和趋势判断）

### 三、重大事件分析
（按时间线梳理关键事件，评估每项事件的影响程度）

### 四、风险提示
（基于文本中提到的风险因素，区分已知风险和潜在风险）

### 五、结论与展望
（综合判断，未来关注要点）

请开始生成报告："""


def build_generation_messages(
    user_query: str,
    retrieved_contexts: str,
    structured_summary: str,
) -> list[dict]:
    """Build the message list for a report generation API call."""
    return [
        {"role": "system", "content": GENERATION_SYSTEM},
        {
            "role": "user",
            "content": GENERATION_USER_TEMPLATE.format(
                user_query=user_query,
                retrieved_contexts=retrieved_contexts,
                structured_summary=structured_summary,
            ),
        },
    ]
