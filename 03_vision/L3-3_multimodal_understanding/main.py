"""L3-3 実践: 画像をマルチモーダルモデルに渡してキャプション＋視覚QA。

同じ画像入力(Chat Completions の content に テキスト＋画像)の上で、
プロンプトを変えるだけで「簡潔キャプション」「物体の列挙(視覚QA)」「alt-text」を作り分ける。
画像は base64 データURIで渡す。認証はキーレス(DefaultAzureCredential)。
"""

import os
import base64
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from dotenv import load_dotenv

load_dotenv()

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
VISION_MODEL = os.getenv("VISION_MODEL", "gpt-4o")  # vision 対応モデルのデプロイ名
IMAGE_PATH = "sample.jpg"

# キーレス認証で Foundry プロジェクトに接続し、OpenAI クライアントを取得
project = AIProjectClient(endpoint=PROJECT_ENDPOINT, credential=DefaultAzureCredential())
client = project.get_openai_client()


def to_data_uri(path: str) -> str:
    """ローカル画像を base64 データURIに変換する。"""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    mime = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime};base64,{b64}"


def ask_about_image(image_path: str, prompt: str) -> str:
    """テキスト＋画像のメッセージを vision 対応モデルに渡し、回答を得る。"""
    res = client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": to_data_uri(image_path)}},
                ],
            }
        ],
    )
    return res.choices[0].message.content


if __name__ == "__main__":
    # 同じ画像に対し、プロンプトを変えるだけで複数の視覚理解タスクを行う
    tasks = {
        "簡潔キャプション": "この画像を一文で簡潔に説明してください。",
        "物体の列挙(視覚QA)": "この画像に写っている主な物体を、箇条書きで列挙してください。",
        "alt-text": "視覚障害者のスクリーンリーダー向けに、この画像のalt-textを1文で作成してください。",
    }
    try:
        for label, prompt in tasks.items():
            print(f"\n===== {label} =====")
            print(ask_about_image(IMAGE_PATH, prompt))
    except Exception as ex:
        print(f"エラー: {ex}")
