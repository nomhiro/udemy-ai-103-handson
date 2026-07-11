"""L2-9 Microsoft Agent Framework で主＋専門エージェントを協調（Magentic）。

マネージャー（主）エージェントが専門エージェント（調査・執筆）を動的に
調整し、成果を統合する。認証はキーレス（AzureCliCredential + az login）。

⚠️ Agent Framework は活発に進化中。クラス名・引数が変わることがあるため、
   実行前に公式サンプルで最新APIを確認すること:
   https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/orchestrations
"""

import os
import asyncio
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.orchestrations import MagenticBuilder
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

load_dotenv()


async def main() -> None:
    # 共有クライアント（キーレス）
    client = FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=AzureCliCredential(),
    )

    # 専門エージェント（役割を分ける）
    researcher = Agent(client=client, name="researcher",
                       instructions="あなたは調査担当。事実と論点を簡潔に集めます。")
    writer = Agent(client=client, name="writer",
                   instructions="あなたは執筆担当。調査結果を分かりやすい日本語にまとめます。")
    # マネージャー（主）エージェント：計画・委譲・調整
    manager = Agent(client=client, name="manager",
                    instructions="あなたは進行役。専門エージェントに委譲し、成果を統合します。")

    # Magentic：マネージャーが専門エージェントを動的に調整
    workflow = MagenticBuilder(
        participants=[researcher, writer],
        manager_agent=manager,
        max_round_count=8,   # 調整ラウンドの上限
        max_stall_count=3,   # 停滞時の再計画上限
    ).build()

    task = "Microsoft Foundry のエージェント機能を、初心者向けに5行で紹介して。"
    async for event in workflow.run_stream(task):
        if getattr(event, "type", None) == "output":
            print(event.data, end="", flush=True)  # 最終成果（マネージャーの統合）
    print()


if __name__ == "__main__":
    asyncio.run(main())
