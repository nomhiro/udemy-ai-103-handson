"""L5-3 実践: カスタムアナライザーで文書から構造化フィールド＋markdown を抽出。

フィールド方式 extract / generate / classify を1つずつ使う。
認証はキーレス（az login + DefaultAzureCredential）。
"""

import os
import time
from azure.identity import DefaultAzureCredential
from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import (
    ContentAnalyzer, ContentFieldSchema, ContentFieldDefinition,
    ContentFieldType, GenerationMethod, AnalysisInput,
)
from dotenv import load_dotenv

load_dotenv()
ENDPOINT = os.environ["CONTENTUNDERSTANDING_ENDPOINT"]
DOCUMENT_URL = os.environ["DOCUMENT_URL"]


def main() -> None:
    client = ContentUnderstandingClient(
        endpoint=ENDPOINT, credential=DefaultAzureCredential())
    analyzer_id = f"l5-3-doc-analyzer-{int(time.time())}"

    # 1) スキーマ定義：extract / generate / classify を1つずつ
    field_schema = ContentFieldSchema(
        name="invoice_schema",
        description="請求書から会社名・合計・要約・種別を抽出",
        fields={
            "company_name": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.EXTRACT,        # 原文を抜き出す
                description="請求元の会社名"),
            "total_amount": ContentFieldDefinition(
                type=ContentFieldType.NUMBER,
                method=GenerationMethod.EXTRACT,
                description="合計金額"),
            "document_summary": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.GENERATE,       # AIが要約を生成
                description="文書の1文要約"),
            "document_type": ContentFieldDefinition(
                type=ContentFieldType.STRING,
                method=GenerationMethod.CLASSIFY,       # 分類
                description="文書の種別",
                enum=["invoice", "receipt", "contract", "other"]),
        },
    )
    analyzer = ContentAnalyzer(
        base_analyzer_id="prebuilt-documentAnalyzer",   # 文書のベースアナライザー
        description="L5-3 custom document analyzer",
        field_schema=field_schema,
    )

    # 2) アナライザー作成（非同期LRO）
    print("アナライザーを作成中...")
    client.begin_create_analyzer(analyzer_id=analyzer_id, resource=analyzer).result()

    try:
        # 3) 解析
        print("文書を解析中...")
        result = client.begin_analyze(
            analyzer_id=analyzer_id,
            inputs=[AnalysisInput(url=DOCUMENT_URL)],
        ).result()

        content = result.contents[0]

        # 4) クリーンな markdown（RAG/エージェント向け）
        print("\n--- markdown（先頭500字）---")
        print((content.markdown or "")[:500])

        # 5) スキーマ準拠のフィールド（自動化/分析向け）＋confidence
        print("\n--- フィールド ---")
        for key in ("company_name", "total_amount", "document_summary", "document_type"):
            f = content.fields.get(key) if content.fields else None
            if f:
                conf = f" (confidence={f.confidence:.2f})" if getattr(f, "confidence", None) else ""
                print(f"  {key}: {f.value}{conf}")
    finally:
        # 6) 後片付け（アナライザー削除）
        client.delete_analyzer(analyzer_id=analyzer_id)
        print(f"\nアナライザー '{analyzer_id}' を削除しました")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 教育目的のエラーハンドリング
        print(f"エラー: {type(e).__name__}: {e}")
        print("Foundry のモデルデプロイ既定が設定されているか、Cognitive Services User ロール、"
              "エンドポイント、DOCUMENT_URL を確認してください。")
        raise
