# FastEasy-DeepResearch - 深度研究报告生成

[![](https://img.shields.io/github/stars/ichont/FastEasy-DeepResearch.svg?style=flat)](https://github.com/ichont/FastEasy-DeepResearch/stargazers)
[![](https://img.shields.io/github/forks/ichont/FastEasy-DeepResearch.svg?style=flat)](https://github.com/ichont/FastEasy-DeepResearch/network/members)
![](https://img.shields.io/github/repo-size/ichont/FastEasy-DeepResearch.svg?style=flat)

FastEasy-DeepResearch是一个基于Agent的智能深度研究报告生成工具，它能够根据您输入的主题，自动在全网搜索相关信息、生成结构化的研究报告，并将其转换为美观的HTML格式，包含交互式图表和数据可视化。

这是一个报告案例demo[关于中国应急管理产业发展的深度研究报告](https://ichont.github.io/FastEasy-DeepResearch/reports/deep_search_report_关于中国应急管理产业发展趋势的深度研究报告_20251208_163443.html)

## 🚀 输入研究主题，即可输出美观的html图文分析报告！

- **智能搜索**：使用Tavily搜索API获取最新、最相关的信息
- **深度分析**：基于LLM（大语言模型）进行深度思考和分析
- **自动结构化**：生成逻辑清晰、层次分明的报告结构
- **可视化图表**：自动生成数据可视化图表，直观展示研究内容
- **美观HTML报告**：生成带有响应式设计的精美HTML报告
- **关键点提取**：自动识别并突出显示报告中的关键信息
- **多格式输出**：同时支持Markdown和HTML两种格式

## 📋 项目结构

```
DeepSearchAgent-Demo/
├── FigHTML/              # 图表生成模块
├── mian/            # 主函数-使用示例
├── img/                  # 项目图片
├── reports/              # 生成的报告默认存储位置
├── src/                  # 源代码目录
│   ├── llms/            # 大语言模型集成
│   ├── nodes/           # 处理节点
│   ├── prompts/         # 提示模板
│   ├── state/           # 状态管理
│   ├── tools/           # 工具函数
│   └── utils/           # 工具类
├── static/               # 静态资源
├── config.py            # 配置文件
├── requirements.txt     # 依赖项
└── README.md            # 项目说明
```

## 🛠️ 安装步骤

### 1. 克隆项目

```bash
git clone <项目地址>
cd FastEasy-DeepResearch
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置API密钥

编辑 `config.py` 文件，填入您的API密钥：

```python
# DeepSeek API Key (必填)
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# OpenAI API Key (可选)
OPENAI_API_KEY = "your_openai_api_key_here"

# Tavily搜索API Key (必填)
TAVILY_API_KEY = "your_tavily_api_key_here"
```

## 📖 使用方法

### 运行示例脚本

```bash
cd main
python main.py
```

## 📊 生成的报告内容

生成的HTML报告包含以下内容：

- **报告标题和摘要**
- **交互式图表**：各章节内容长度统计
- **结构化章节**：每个章节包含详细内容
- **关键要点**：自动提取的重要信息
- **响应式设计**：适配各种设备屏幕
- **交互功能**：展开/收起章节内容

## 🔧 配置选项

在 `config.py` 中可以配置以下选项：

```python
# LLM配置
DEFAULT_LLM_PROVIDER = "deepseek"  # 可选: "deepseek", "openai"
DEEPSEEK_MODEL = "deepseek-chat"    # DeepSeek模型
OPENAI_MODEL = "gpt-4o-mini"        # OpenAI模型

# 搜索配置
MAX_REFLECTIONS = 2                  # 深度思考次数
SEARCH_RESULTS_PER_QUERY = 3         # 每次搜索返回的结果数
SEARCH_CONTENT_MAX_LENGTH = 20000    # 搜索内容最大长度

# 输出配置
OUTPUT_DIR = "reports"               # 报告输出目录
SAVE_INTERMEDIATE_STATES = True      # 是否保存中间状态

# RAG配置
ENABLE_RAG = True                    # 是否启用RAG增强搜索
RAG_TOP_K = 5                        # RAG返回的最相关文档数量
```

## 🎯 示例

### 在main.py中输入主题

```
中国应急管理产业发展趋势
```

### 输出报告

- Markdown格式：`reports/deep_search_report_中国应急管理产业发展趋势_20251208_163443.md`
- HTML格式：`reports/deep_search_report_关于中国应急管理产业发展趋势的深度研究报告_20251208_163443.html`

## 🔍 工作流程

1. **生成报告结构**：基于输入主题生成报告大纲
2. **深度搜索**：对每个章节进行多次搜索和思考
3. **内容整合**：将搜索结果整合为连贯的内容
4. **报告格式化**：生成最终的Markdown报告
5. **HTML转换**：将Markdown转换为美观的HTML格式
6. **数据可视化**：添加交互式图表和可视化元素

## 📝 注意事项

- 请确保您的API密钥有效且有足够的配额
- 网络连接不稳定可能会影响搜索结果
- 生成报告的时间取决于主题复杂度和网络速度
- 您可以通过调整配置来优化报告质量和生成速度

## 🤝 感谢

感谢[伟岸纵横](https://www.vrgvtech.com/)提供的API和算力服务

感谢[DeepSearchAgent-Demo](https://github.com/666ghj/DeepSearchAgent-Demo)提供的思路与参考

## 📄 许可证

本项目采用MIT许可证。

## 📧 联系方式

如有问题或建议，请随时联系我们。
