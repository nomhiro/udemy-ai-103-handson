# L2-3 Foundry IQ ハンズオン（ポータル主体）

このレッスンは **Microsoft Foundry ポータル**での操作が主体です（PoC は無料枠で最短）。コードよりも、knowledge base を作ってエージェントに接続する一連の流れを体験します。

## ポータル手順（推奨）
1. **Foundry ポータル**（https://ai.azure.com）にサインイン。**New Foundry** トグルを ON。
2. プロジェクトを作成/選択 → 上部 **Build**。
3. **Knowledge** タブ：
   - agentic retrieval 対応の **Azure AI Search サービス**を作成/接続。
   - **knowledge source** を1つずつ追加して **knowledge base** を作成。
   - **reasoning effort**（minimal/low/medium）を設定（複雑クエリは medium）。
4. **Agents** タブ：
   - エージェントを作成 → 作成した **knowledge base を接続**。
   - システムプロンプト（`agent_instructions.txt` 参照）を設定。
5. **playground** で、取り込んだデータにしかない情報を質問し、出典付き回答を確認。

## プログラム接続（MCP 経由・概観）
- knowledge sources → knowledge base 作成（Azure AI Search 側）。
- プロジェクトに **RemoteTool** の project connection を作成（マネージドIDで KB の MCP エンドポイントを指す）。
- エージェントに **MCP ツール**を追加（KB は `knowledge_base_retrieve` MCP ツールを公開）。
- 詳細：https://learn.microsoft.com/azure/foundry/agents/how-to/foundry-iq-connect
- E2E サンプル：https://github.com/Azure-Samples/azure-search-python-samples/tree/main/agentic-retrieval-pipeline-example

## 後片付け
- knowledge base / knowledge source / エージェントを削除。
- Azure AI Search サービスを削除（無料枠でも枠を占有）。検証専用ならリソースグループごと削除。

> ⚠️ ロール名リネーム：**Foundry User / Foundry Project Manager**（旧 Azure AI User / Azure AI Project Manager。権限は不変）。
