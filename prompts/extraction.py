"""Extraction prompt templates for DeepSeek API."""

EXTRACTION_SYSTEM = """你是一个专业的中文财务数据抽取专家。你的任务是从非结构化的中文商业文本中抽取出结构化的关键字段。

你必须遵守以下规则：
1. 只抽取文本中明确出现的信息，不要推测或编造数据
2. 如果某个字段在文本中不存在，将其值设为 null
3. 数字字段（revenue, net_profit, growth_rate）必须转换为数值类型，去掉"亿"、"万"等单位
4. 日期字段必须统一为 YYYY-MM-DD 格式
5. 对每个抽取结果提供一个 confidence_score (0.0-1.0)，表示你对该字段抽取的置信度
6. key_persons 必须是字符串数组格式
7. 必须返回合法的 JSON，不要包含任何 JSON 之外的文本"""

EXTRACTION_USER_TEMPLATE = """请从以下文本中抽取关键财务和商业信息：

---
{chunk_text}
---

请以 JSON 格式返回抽取结果，字段说明如下：
- company_name: 公司全称 (string or null)
- industry: 所属行业 (string or null)
- revenue: 营业收入数值，纯数字不含单位 (number or null)
- revenue_unit: 营收单位，如"亿元"、"万元" (string or null)
- revenue_period: 营收对应期间，如"2024"、"2024H1" (string or null)
- net_profit: 净利润数值，纯数字不含单位 (number or null)
- net_profit_unit: 净利润单位 (string or null)
- net_profit_period: 净利润对应期间 (string or null)
- growth_rate: 同比增长率，百分比数值，如18.5表示18.5% (number or null)
- event_date: 重大事件日期，YYYY-MM-DD格式 (string or null)
- event_summary: 事件简述，不超过50字 (string or null)
- key_persons: 关键人物姓名列表 (list of strings or null)
- location: 主要地点/城市 (string or null)
- stock_code: 股票代码 (string or null)
- stock_exchange: 交易所代码，如"SZ"、"SH"、"HK" (string or null)
- confidence_score: 整体抽取置信度 (number, 0.0-1.0)

抽取示例：
文本："2024年，北京智行科技有限公司实现营业收入125.6亿元，同比增长22.3%。"
输出：{{"company_name":"北京智行科技有限公司","industry":null,"revenue":125.6,"revenue_unit":"亿元","revenue_period":"2024","net_profit":null,"net_profit_unit":null,"net_profit_period":null,"growth_rate":22.3,"event_date":null,"event_summary":null,"key_persons":null,"location":"北京","stock_code":null,"stock_exchange":null,"confidence_score":0.85}}

仅返回 JSON，不要输出其他内容："""


def build_extraction_messages(chunk_text: str) -> list[dict]:
    """Build the message list for an extraction API call."""
    return [
        {"role": "system", "content": EXTRACTION_SYSTEM},
        {"role": "user", "content": EXTRACTION_USER_TEMPLATE.format(chunk_text=chunk_text)},
    ]
