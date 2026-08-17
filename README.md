# udemy-ai-103-handson

Udemy 講座 **「AI-103 Developing AI Apps and Agents 試験対策講座」** の **実践編（ハンズオン）コード集**です。各レクチャーで講師と一緒に手を動かすための Python サンプルが、セクション／レッスン単位で入っています。

> 受講者の方は、このリポジトリを **Fork** してから clone するのがおすすめです（自分の変更を GitHub に残せます）。**clone だけ、または ZIP ダウンロードでもハンズオンは実施できます。** Fork が必須なのは **CI/CD の実践（`01_plan_manage/L1-3_deploy_cicd` の GitHub Actions）** だけで、それも実行は任意です。

> 🆘 **うまく動かないときは、まず [FAQ.md](FAQ.md) を見てください。** クォータ不足（`insufficient quota`）・認証エラー・デプロイ名の取り違えなど、全レッスン共通のつまずきと対処をまとめてあります。

## 前提環境
- **Azure サブスクリプション**（従量課金。一部 Preview 機能はリージョン/申請制約あり）
  - ⚠️ **作りたてのサブスクリプションでは、最新世代モデルのデプロイが `insufficient quota` で失敗することがあります。** Foundry はサブスクリプションごとに**クォータティア**（最下位＝Free Tier / Tier 0 〜 Tier 6）を割り当てており、最下位ティアで既定クォータが付くのは `gpt-4.1-mini` / `gpt-5-mini` / `o4-mini` / `text-embedding-3-small` の4モデルだけです。各レッスンの `.env` はモデル名を環境変数にしてあるので、**使えるモデルに差し替えればハンズオンは実施できます**（→ [FAQ.md](FAQ.md#1-モデルがデプロイできないisnt-available-due-to-insufficient-quota)）。**リージョンを変えても解決しません。**
- **Microsoft Foundry** プロジェクト（ポータル：https://ai.azure.com ）
- **Python 3.11+** ／ 仮想環境（venv）／ VS Code（推奨：Dev Container）
- **Azure CLI**（`az login`）＋ Microsoft Entra ID 認証（**キーレス**を第一選択）

## 使い方
1. このリポジトリを **Fork** し、自分のアカウントから clone する（Fork せず、この URL をそのまま clone してもかまいません）。
   ```bash
   git clone https://github.com/<your-account>/udemy-ai-103-handson.git
   cd udemy-ai-103-handson
   ```
   > Git を入れていない場合は、緑の **Code** ボタン → **Download ZIP** で取得して展開しても進められます。
   > Fork した教材を後から最新にするには、GitHub の **Sync fork** を押してから `git pull` します。
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
- ハンズオンは**実課金**が発生しますが、**モデルの従量デプロイは置いておくだけでは課金されません**（課金は呼び出したトークン分）。学習を続けるなら、作ったリソースは次のレッスンで使い回してかまいません。
- ⚠️ **常時課金が発生するリソース**（Provisioned/PTU デプロイ、Azure AI Search、Container Apps など）を作るレッスンでは、手順末尾に**後片付け**を明記しています。そこだけは忘れずに実施してください。

## 関連
- 本リポジトリは Udemy 講座の教材です。解説（座学）と手順の詳細は講座本編・各レクチャー資料を参照してください。
