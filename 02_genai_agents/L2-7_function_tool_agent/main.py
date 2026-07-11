"""L2-7 自作関数を FunctionTool でエージェントに登録して使わせる。

FunctionTool でスキーマを宣言し、エージェント定義に登録。
function_call → アプリが実行 → function_call_output → 最終回答 のループ。
エラーもモデルに返す。認証はキーレス。finally で後片付け。
"""

import os
import json
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput
from dotenv import load_dotenv

load_dotenv()
PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
MODEL_DEPLOYMENT = os.getenv("MODEL_DEPLOYMENT", "gpt-4.1-mini")

# --- 自作関数の実体（アプリ側で実行。モック） ---
_STOCK = {"X1": 3, "X2": 0, "M27": 12}


def get_inventory(product_code: str) -> dict:
    """商品コードの在庫数を返す"""
    if product_code not in _STOCK:
        return {"error": f"unknown product_code: {product_code}"}  # エラーもモデルに返す
    return {"product_code": product_code, "stock": _STOCK[product_code]}


# --- FunctionTool でスキーマを宣言 ---
inv_tool = FunctionTool(
    name="get_inventory",
    description="商品コードの在庫数を取得する。型番が分かるときに使う。",
    parameters={
        "type": "object",
        "properties": {"product_code": {"type": "string", "description": "商品コード（例 X1）"}},
        "required": ["product_code"],
        "additionalProperties": False,
    },
    strict=True,
)


def main() -> None:
    if not PROJECT_ENDPOINT:
        raise SystemExit("PROJECT_ENDPOINT が未設定です。.env を確認してください。")

    project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
    openai = project.get_openai_client()

    agent = None
    try:
        agent = project.agents.create_version(
            agent_name="inventory-agent",
            definition=PromptAgentDefinition(
                model=MODEL_DEPLOYMENT,
                instructions="在庫を聞かれたら get_inventory ツールで調べて日本語で答えてください。",
                tools=[inv_tool],
            ),
        )
        print(f"エージェント作成: {agent.name} v{agent.version}")

        conversation = openai.conversations.create()
        ref = {"agent_reference": {"name": agent.name, "type": "agent_reference"}}

        # 1) 質問 → モデルが function_call を返す
        res = openai.responses.create(
            input="商品 X1 の在庫はいくつ？", conversation=conversation.id, extra_body=ref)

        # 2) function_call を処理（アプリが実行）
        input_list = []
        for item in res.output:
            if getattr(item, "type", None) == "function_call" and item.name == "get_inventory":
                args = json.loads(item.arguments)
                result = get_inventory(**args)  # 実行するのはアプリ
                print(f"[ツール呼び出し] get_inventory({args}) -> {result}")
                input_list.append(FunctionCallOutput(
                    type="function_call_output", call_id=item.call_id,
                    output=json.dumps(result, ensure_ascii=False)))

        # 3) 結果を返して最終回答
        if input_list:
            final = openai.responses.create(
                input=input_list, conversation=conversation.id, extra_body=ref)
            print(f"AI> {final.output_text}")
        else:
            print(f"AI> {res.output_text}")

    except Exception as ex:  # 教育目的の素朴なエラーハンドリング
        print(f"[エラー] {ex}")
    finally:
        if agent:
            project.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("エージェントを削除しました")


if __name__ == "__main__":
    main()
