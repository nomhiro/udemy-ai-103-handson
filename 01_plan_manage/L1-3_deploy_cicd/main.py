"""L1-3 実践: デプロイの「動作確認（スモークテスト）」をキーレスで行う。

CLI または Bicep で作成したモデルデプロイが、実際に推論できる状態かを確認する。
- 認証はキーレス（DefaultAzureCredential / az login 済みの資格情報）。APIキーは使わない。
- 渡すのは「デプロイ名」（カタログ名ではない点に注意）。
"""
import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

# Bicep/CLI の出力（エンドポイント）と、付けたデプロイ名を .env に転記しておく
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME", "chat")

PROMPT = "デプロイの動作確認です。「OK」とだけ短く返してください。"


def main():
    if not PROJECT_ENDPOINT:
        print("[エラー] PROJECT_ENDPOINT が未設定です。.env を確認してください。")
        return

    try:
        # Microsoft Foundry プロジェクトへ接続（キーレス）
        project = AIProjectClient(
            endpoint=PROJECT_ENDPOINT,
            credential=DefaultAzureCredential(),
        )
        openai = project.get_openai_client()

        # デプロイ名（=model パラメータ）で推論。例外なく出力が返ればデプロイは健全
        res = openai.responses.create(model=DEPLOYMENT_NAME, input=PROMPT)

        print(f"===== デプロイ '{DEPLOYMENT_NAME}' のスモークテスト =====")
        print(f"出力: {res.output_text}")
        usage = getattr(res, "usage", None)
        if usage:
            print(f"入力トークン: {usage.input_tokens} / 出力トークン: {usage.output_tokens}")
        print("✅ デプロイは正常に推論できています。")

    except Exception as ex:
        print(f"[エラー] デプロイのスモークテストに失敗: {ex}")
        print("ヒント: デプロイ名・エンドポイント・az login・RBAC ロール（Cognitive Services User 等）を確認。")


if __name__ == "__main__":
    main()
