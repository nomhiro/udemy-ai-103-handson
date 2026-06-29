# udemy-ai-103-handson

Udemy 講座 **「AI-103 Developing AI Apps and Agents 試験対策講座」** の **実践編（ハンズオン）コード集**です。各レクチャーで講師と一緒に手を動かすための Python サンプルが、セクション／レッスン単位で入っています。

> 受講者の方は、このリポジトリを **Fork** して自分の環境で作業してください。

## 前提環境
- **Azure サブスクリプション**（従量課金。一部 Preview 機能はリージョン/申請制約あり）
- **Microsoft Foundry** プロジェクト（ポータル：https://ai.azure.com ）
- **Python 3.11+** ／ 仮想環境（venv）／ VS Code（推奨：Dev Container）
- **Azure CLI**（`az login`）＋ Microsoft Entra ID 認証（**キーレス**を第一選択）

## 使い方
1. このリポジトリを **Fork** し、自分のアカウントに clone する。
   ```bash
   git clone https://github.com/<your-account>/udemy-ai-103-handson.git
   cd udemy-ai-103-handson
   ```
2. 取り組むレッスンのフォルダへ移動し、仮想環境と依存をセットアップ。
   ```bash
   cd 01_plan_manage/L1-1_model_selection
   python -m venv .venv
   . .venv/Scripts/activate        # macOS/Linux は: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. `.env.sample` を `.env` にコピーして値を設定（エンドポイント等。**APIキーは使わずキーレス**が基本）。
   ```bash
   cp .env.sample .env             # Windows: copy .env.sample .env
   ```
4. `az login` 済みであることを確認して実行。
   ```bash
   python main.py
   ```

## ディレクトリ構成
```
udemy-ai-103-handson/
├── 00_intro/
├── 01_plan_manage/           # セクション1：計画と管理
│   └── L1-1_model_selection/ # 各レッスン＝独立して実行可能
│       ├── main.py
│       ├── .env.sample
│       └── requirements.txt
├── 02_genai_agents/          # セクション2：生成AI・エージェント
├── 03_vision/                # セクション3：コンピュータービジョン
├── 04_text/                  # セクション4：テキスト分析
└── 05_info_extraction/       # セクション5：情報抽出
```
（レッスンは順次追加されます。）

## セキュリティ・コストの注意
- **`.env` はコミットしない**（`.gitignore` 済み）。資格情報はキーレス（Entra ID）または Azure Key Vault を推奨。
- ハンズオンは**実課金**が発生します。各レッスンの手順末尾にある**後片付け（リソース削除）**を実施してください。

## 関連
- 本リポジトリは Udemy 講座の教材です。解説（座学）と手順の詳細は講座本編・各レクチャー資料を参照してください。
