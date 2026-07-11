# L5-1 検索・グラウンディング：エンリッチしたインデックス → エージェント接続

スキルセット（Text Split + Azure OpenAI Embedding = integrated vectorization）で
Blob のサンプル文書をチャンク化・ベクトル化してインデックス化し、
そのインデックスを Foundry エージェントの **Azure AI Search ツール**として接続して、
引用つきでグラウンディング回答させるハンズオン。

## 前提リソース
- Azure AI Search（Basic 以上推奨）
- Microsoft Foundry プロジェクト ＋ Azure OpenAI 埋め込みモデル（例 `text-embedding-3-large`）＋ チャットモデル（例 `gpt-4.1-mini`）
- Azure Blob Storage（サンプル文書コンテナ）

## RBAC（キーレス。自分と各マネージドIDに付与）
- 検索サービス：`Search Service Contributor` ＋ `Search Index Data Contributor`
- ストレージ：（検索サービスのマネージドIDに）`Storage Blob Data Reader`
- Azure OpenAI：（検索サービスのマネージドIDに）`Cognitive Services OpenAI User`

## 手順
```bash
python -m venv .venv && source .venv/bin/activate   # Windows は .venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env   # 値を埋める
az login

# サンプル文書を Blob にアップロード
az storage blob upload-batch -d l5-1-docs -s ./docs --account-name <account> --auth-mode login

# 1) エンリッチインデックスを作成・実行
python 01_build_index.py

# 2) （Foundry ポータルで Azure AI Search 接続を作成後）エージェントに接続して質問
python 02_ask_agent.py
```

## 後片付け
検索オブジェクト（indexer → skillset → index → data source）と、検証用に作ったリソースを削除する。
検証専用ならリソースグループごと削除が確実。

> ⚠️ SDK のモデルクラス名・API バージョン・埋め込みモデル ID は変化が速い。
> `pip show azure-search-documents` と公式ドキュメントで最新を確認すること。
