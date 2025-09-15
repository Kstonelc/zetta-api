from huggingface_hub import list_models, model_info, HfApi
import time

# 可选 API token（匿名也能访问部分）
api = HfApi()


orgs = [
    # "meta-llama",
    # "mistralai",
    # "baichuan-inc",
    "Qwen",
    # "THUDM",
    # "internlm",
    # "deepseek-ai",
    # "openchat",
    # "01-ai",
    # "HuggingFaceH4",
]

for org in orgs:
    print(f"📦 获取组织：{org}")
    models = api.list_models(
        author=org, limit=10, sort="downloads", filter="text-generation"
    )  # 可调更大

    for m in models:
        try:
            info = model_info(m.modelId)
            config = info.config or {}

            print(f"✔ 模型: {m.modelId}")
            print(f"  - 架构: {config.get('architectures', ['未知'])[0]}")
            print(f"  - 任务类型: {info.pipeline_tag}")
            print(f"  - 参数量: {config.get('num_parameters', '未知')}")
            print(f"  - 更新时间: {info.lastModified}")
            print(f"  - 链接: https://huggingface.co/{m.modelId}")
            print("-" * 60)
        except Exception as e:
            print(f"❌ 获取失败: {m.modelId}, 错误: {e}")
