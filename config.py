# Deep Search Agent 配置文件
# 请在这里填入您的API密钥

# DeepSeek API Key
DEEPSEEK_API_KEY = "sk-eead4e31663d42e4ad09584dc4346779"

# OpenAI API Key (可选)
OPENAI_API_KEY = "your_openai_api_key_here"

# Tavily搜索API Key
TAVILY_API_KEY = "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"

# 配置参数
DEFAULT_LLM_PROVIDER = "deepseek"
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True

# RAG配置
ENABLE_RAG = True
RAG_TOP_K = 5
RAG_EMBEDDING_PROVIDER = "openai"
