"""L2-8 リモート MCP サーバーのツールをエージェントに接続して呼ぶ。

MCPTool でリモート MCP サーバー（例：GitHub）を宣言し、require_approval で
承認フロー（mcp_approval_request → mcp_approval_response）を処理する。
認証は project_connection_id（最小権限）。finally で後片付け。
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from openai.types.responses.response_input_param import McpApprovalResponse
from dotenv import load_dotenv

load_dotenv()
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-5-mini")
MCP_CONNECTION_NAME = os.getenv("MCP_CONNECTION_NAME")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "https://api.githubcopilot.com/mcp")


def main() -> None:
    if not PROJECT_ENDPOINT or not MCP_CONNECTION_NAME:
        raise SystemExit("PROJECT_ENDPOINT / MCP_CONNECTION_NAME を .env に設定してください。")

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    openai = project.get_openai_client()

    # リモート MCP サーバーをツールとして宣言（承認を必須に）
    tool = MCPTool(
        server_label="github",
        server_url=MCP_SERVER_URL,
        require_approval="always",
        project_connection_id=MCP_CONNECTION_NAME,
    )

    agent = None
    try:
        agent = project.agents.create_version(
            agent_name="mcp-agent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT,
                instructions="必要に応じて MCP ツールを使ってください。",
                tools=[tool],
            ),
        )
        print(f"エージェント作成: {agent.name} v{agent.version}")

        conversation = openai.conversations.create()
        ref = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}

        # 1) 質問 → MCP 呼び出しの承認要求が返る
        response = openai.responses.create(
            conversation=conversation.id, input="私の GitHub のユーザー名は？", extra_body=ref)

        # 2) 承認要求を処理（内容を確認して承認/拒否）
        input_list = []
        for item in response.output:
            if getattr(item, "type", None) == "mcp_approval_request" and item.id:
                print(f"[承認要求] server={item.server_label} tool={getattr(item, 'name', '?')}")
                approve = input("このMCPツール呼び出しを承認しますか？ (y/N): ").strip().lower() == "y"
                input_list.append(McpApprovalResponse(
                    type="mcp_approval_response", approve=approve, approval_request_id=item.id))

        # 3) 承認応答を返して処理を続ける
        if input_list:
            response = openai.responses.create(
                input=input_list, previous_response_id=response.id, extra_body=ref)
        print(f"AI> {response.output_text}")

    except Exception as ex:  # 教育目的の素朴なエラーハンドリング
        print(f"[エラー] {ex}")
    finally:
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("エージェントを削除しました")


if __name__ == "__main__":
    main()
