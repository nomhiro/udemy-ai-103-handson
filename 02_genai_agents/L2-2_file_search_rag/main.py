"""L2-2 File Search ツールで PDF/Markdown にグラウンディングする RAG。

ベクトルストア作成 → 文書アップロード（自動チャンク化・ベクトル化）→
File Search ツール付きエージェント作成 → 文書に基づく出典付き回答。
認証はキーレス（DefaultAzureCredential + az login）。
File Search は追加課金あり。finally で必ず後片付けする。
"""

import os
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-5-mini")
DOC_PATH = Path(os.getenv("DOC_PATH", "product_info.md")).resolve()
QUESTION = os.getenv("QUESTION", "この製品の保証期間と対応OSを教えて。")


def main() -> None:
    if not PROJECT_ENDPOINT:
        raise SystemExit("PROJECT_ENDPOINT が未設定です。.env を確認してください。")
    if not DOC_PATH.exists():
        raise SystemExit(f"文書が見つかりません: {DOC_PATH}")

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    openai = project.get_openai_client()

    agent = None
    vector_store = None
    try:
        # 1) ベクトルストアを作り、文書をアップロード（自動でチャンク化・ベクトル化）
        vector_store = openai.vector_stores.create(name="ProductInfoStore")
        with DOC_PATH.open("rb") as fh:
            openai.vector_stores.files.upload_and_poll(vector_store_id=vector_store.id, file=fh)
        print(f"ベクトルストア作成・取り込み完了 (id: {vector_store.id})")

        # 2) File Search ツールを持つエージェントを作る
        agent = project.agents.create_version(
            agent_name="FileSearchRagAgent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT,
                instructions=(
                    "あなたはアップロードされた文書に基づいて回答するアシスタントです。"
                    "file search で根拠を探し、出典を示して日本語で答えてください。"
                ),
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="File Search による RAG エージェント",
        )

        # 3) 会話を作り、文書にしかない情報を質問する
        conversation = openai.conversations.create()
        response = openai.responses.create(
            conversation=conversation.id,
            input=QUESTION,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        print("\n=== 回答 ===")
        print(response.output_text)

    except Exception as ex:  # 教育目的の素朴なエラーハンドリング
        print(f"[エラー] {ex}")
    finally:
        # 4) 後片付け（課金リソースを削除）
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        if vector_store:
            openai.vector_stores.delete(vector_store.id)
        print("後片付け完了（エージェント・ベクトルストアを削除）")


if __name__ == "__main__":
    main()
