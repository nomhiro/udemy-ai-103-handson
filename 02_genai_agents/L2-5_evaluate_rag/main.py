"""L2-5 RAG の回答を評価器でスコア化する。

azure-ai-evaluation の evaluate() で Groundedness/Relevance/Coherence を
data.jsonl に対してまとめて実行し、スコアで品質を可視化する。
AI-assisted 評価器は judge となる LLM（model_config）が必要。
"""

import os
from azure.ai.evaluation import (
    evaluate, GroundednessEvaluator, RelevanceEvaluator, CoherenceEvaluator,
)
from dotenv import load_dotenv

load_dotenv()

# AI-assisted 評価器が使う judge LLM
model_config = {
    "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "azure_deployment": os.getenv("JUDGE_DEPLOYMENT", "gpt-4.1"),
    "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
}


def main() -> None:
    if not model_config["azure_endpoint"]:
        raise SystemExit("AZURE_OPENAI_ENDPOINT が未設定です。.env を確認してください。")

    groundedness = GroundednessEvaluator(model_config)
    relevance = RelevanceEvaluator(model_config)
    coherence = CoherenceEvaluator(model_config)

    result = evaluate(
        data="data.jsonl",
        evaluators={
            "groundedness": groundedness,
            "relevance": relevance,
            "coherence": coherence,
        },
    )

    print("=== 集計 ===")
    for k, v in result.get("metrics", {}).items():
        print(f"{k}: {v}")
    print("\n=== 各サンプル ===")
    for row in result.get("rows", []):
        print(row)


if __name__ == "__main__":
    main()
