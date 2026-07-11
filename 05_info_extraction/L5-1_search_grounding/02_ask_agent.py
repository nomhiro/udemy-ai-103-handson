"""L5-1 実践(2/2): 作ったインデックスを Azure AI Search ツールとしてエージェントに接続。

引用つきで回答させる。事前に Foundry ポータルで Azure AI Search への接続を作っておく
（SEARCH_CONNECTION_NAME）。認証はキーレス（az login + DefaultAzureCredential）。
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchTool, PromptAgentDefinition,
    AzureAISearchToolResource, AISearchIndexResource, AzureAISearchQueryType,
)
from dotenv import load_dotenv

load_dotenv()


def main() -> None:
    project = AIProjectClient(endpoint=os.environ["PROJECT_ENDPOINT"],
                              credential=DefaultAzureCredential())
    openai = project.get_openai_client()

    # 接続名 → 接続IDを解決
    conn_id = project.connections.get(os.environ["SEARCH_CONNECTION_NAME"]).id

    agent = project.agents.create_version(
        agent_name="L5-1-GroundingAgent",
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT"],
            instructions=("あなたは製品サポートのアシスタントです。必ず検索ツールの結果のみを根拠に答え、"
                          "出典を [message_idx:search_idx†source] 形式で示してください。"),
            tools=[AzureAISearchTool(azure_ai_search=AzureAISearchToolResource(indexes=[
                AISearchIndexResource(
                    project_connection_id=conn_id,
                    index_name=os.environ["SEARCH_INDEX_NAME"],
                    query_type=AzureAISearchQueryType.VECTOR_SEMANTIC_HYBRID,
                )]))],
        ),
    )
    print(f"agent created: {agent.name} v{agent.version}")

    try:
        question = "保証期間は何年ですか？ 出典も教えてください。"
        stream = openai.responses.create(
            stream=True, tool_choice="required", input=question,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )
        for event in stream:
            if event.type == "response.output_text.delta":
                print(event.delta, end="")
            elif event.type == "response.completed":
                print(f"\n--- 完了 ---\n{event.response.output_text}")
    finally:
        # 後片付け（エージェントのバージョンを削除）
        project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
        print("\nagent deleted")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 教育目的のエラーハンドリング
        print(f"エラー: {type(e).__name__}: {e}")
        print("接続（SEARCH_CONNECTION_NAME）と RBAC（Search Index Data Contributor / "
              "Search Service Contributor）、インデックス名（大文字小文字）を確認してください。")
        raise
