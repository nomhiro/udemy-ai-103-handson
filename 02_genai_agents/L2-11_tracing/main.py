"""L2-11 エージェントにトレースを仕込み、失敗ケースを観測して原因分析。

server-side トレース（App Insights 接続）＋ client-side 計装（OpenTelemetry）。
わざと存在しない型番を照会してツールが error を返す失敗を起こし、
Foundry ポータルの Traces で span を辿って原因を分析する。
認証はキーレス。finally で後片付け。
"""

import os
import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv

load_dotenv()
# プロンプト内容もトレースに記録（個人情報に注意）
os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true"

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-4.1-mini")

_STOCK = {"X1": 3}


def get_inventory(product_code: str) -> dict:
    if product_code not in _STOCK:
        return {"error": f"unknown product_code: {product_code}"}  # 失敗を再現
    return {"product_code": product_code, "stock": _STOCK[product_code]}


def main() -> None:
    if not PROJECT_ENDPOINT:
        raise SystemExit("PROJECT_ENDPOINT が未設定です。.env を確認してください。")

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())

    # client-side 計装：接続済み App Insights へテレメトリを送る
    conn = project.telemetry.get_application_insights_connection_string()
    configure_azure_monitor(connection_string=conn)

    openai = project.get_openai_client()

    tool = FunctionTool(
        name="get_inventory", description="在庫数を取得",
        parameters={"type": "object", "properties": {"product_code": {"type": "string"}},
                    "required": ["product_code"], "additionalProperties": False}, strict=True)

    agent = None
    try:
        agent = project.agents.create_version(
            agent_name="traced-agent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT,
                instructions="在庫照会には get_inventory を使ってください。", tools=[tool]))
        conversation = openai.conversations.create()
        ref = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}

        # わざと存在しない型番（ZZ9）を照会 → ツールが error を返す失敗ケース
        res = openai.responses.create(input="ZZ9 の在庫は？", conversation=conversation.id, extra_body=ref)
        input_list = []
        for item in res.output:
            if getattr(item, "type", None) == "function_call":
                result = get_inventory(**json.loads(item.arguments))
                print(f"[tool] {item.name} -> {result}")
                input_list.append(FunctionCallOutput(
                    type="function_call_output", call_id=item.call_id,
                    output=json.dumps(result, ensure_ascii=False)))
        if input_list:
            final = openai.responses.create(input=input_list, conversation=conversation.id, extra_body=ref)
            print(f"AI> {final.output_text}")
        print("Foundry ポータルの Agents → Traces で trace を確認（取り込みに数分）")
    finally:
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)


if __name__ == "__main__":
    main()
