"""L1-5 実践 (2): OpenAI SDK + トークンプロバイダーでモデルを直接呼ぶ／キー方式と対比。

main.py は Foundry プロジェクト経由だったが、こちらは Foundry Models の
リソースエンドポイント(<resource>.openai.azure.com/openai/v1/)を OpenAI SDK で直接叩く。
キーレスの仕組み（api_key の代わりに Entra ID トークンプロバイダーを渡す）を最小コードで示す。

ポイント:
- get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default")
  が、呼び出しのたびに自動でトークンを供給する（= api_key にこれを渡す）。
- 比較として「APIキーで呼ぶ」関数も用意。local auth を無効化(disableLocalAuth)した後は
  キー方式が 401 で失敗することを体感する（assign_role_disable_key.azcli 実行後に確認）。

必要ロール: Foundry リソースに対する「Cognitive Services User」(直接推論用)。
"""

import os

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# 形式: https://<resource>.openai.azure.com/openai/v1/  (または .services.ai.azure.com/openai/v1/)
BASE_URL = os.getenv("FOUNDRY_OPENAI_BASE_URL")
MODEL = os.getenv("MODEL_DEPLOYMENT", "gpt-4.1")
API_KEY = os.getenv("FOUNDRY_API_KEY")  # 比較用(任意)。キーレスでは未設定でよい
PROMPT = "あなたは何で認証されていますか？1文で。"


def call_keyless() -> str:
    """キーレス: api_key にトークンプロバイダーを渡す（鍵は持たない）。"""
    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://ai.azure.com/.default",  # Foundry(Azure AI)向けトークンのスコープ
    )
    client = OpenAI(base_url=BASE_URL, api_key=token_provider)
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return res.choices[0].message.content


def call_with_key() -> str:
    """比較用: APIキー方式。local auth 無効化後は 401 になるはず。"""
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
    res = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT}],
    )
    return res.choices[0].message.content


def main() -> None:
    if not BASE_URL:
        print("FOUNDRY_OPENAI_BASE_URL が未設定です。.env を確認してください。")
        return

    print("===== 方式A: キーレス (Entra ID トークンプロバイダー) =====")
    try:
        print(call_keyless())
    except Exception as ex:
        print(f"  失敗: {type(ex).__name__}: {ex} (403ならロール『Cognitive Services User』を確認)")

    if API_KEY:
        print("\n===== 方式B: APIキー (比較用) =====")
        try:
            print(call_with_key())
        except Exception as ex:
            print(f"  失敗: {type(ex).__name__}: {ex}")
            print("  → disableLocalAuth を有効化済みなら、これは期待どおりの 401 です。")
    else:
        print("\n(FOUNDRY_API_KEY 未設定のため方式Bはスキップ。キーレス運用ではこれでOK)")


if __name__ == "__main__":
    main()
