"""L1-1 実践: 2モデル（大/小）を同一タスクで比較する。

同じプロンプトを「大きいモデル」と「小さいモデル」に投げ、
出力・レイテンシ・トークン数（≒コスト）を並べて比較する。
認証はキーレス（DefaultAzureCredential / az login 済みの資格情報）。
"""
import os
import time

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_LARGE = os.getenv("MODEL_LARGE", "gpt-5.4")
MODEL_SMALL = os.getenv("MODEL_SMALL", "gpt-5.4-nano")

# 比較用の共通プロンプト（同一タスク）
PROMPT = "Azure の Microsoft Foundry とは何かを、初心者向けに3文で説明してください。"

# Microsoft Foundry プロジェクトへ接続（Responses API クライアントを取得）
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
openai = project.get_openai_client()

# 比較用の関数
def run(model: str):
    t0 = time.perf_counter()
    res = openai.responses.create(model=model, input=PROMPT)
    elapsed = time.perf_counter() - t0
    usage = getattr(res, "usage", None)
    in_tok = getattr(usage, "input_tokens", None) if usage else None
    out_tok = getattr(usage, "output_tokens", None) if usage else None
    return res.output_text, elapsed, in_tok, out_tok


def main():
    for label, model in [("大 (LARGE)", MODEL_LARGE), ("小 (SMALL)", MODEL_SMALL)]:
        try:
            text, elapsed, in_tok, out_tok = run(model)
            print(f"\n===== {label}: {model} =====")
            print(f"レイテンシ: {elapsed:.2f}s / 入力トークン: {in_tok} / 出力トークン: {out_tok}")
            print(f"出力:\n{text}")
        except Exception as ex:
            print(f"[{label}:{model}] エラー: {ex}")


if __name__ == "__main__":
    main()
