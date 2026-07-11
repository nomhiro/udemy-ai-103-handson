# L1-3 実践: Foundry でのソリューション構築（インフラ／デプロイ／CI-CD）

モデルデプロイを **CLI／Bicep（IaC）で再現**し、**スモークテスト**で動作確認、さらに **GitHub Actions の雛形**で「評価ゲート → デプロイ」の流れを体験するハンズオンです。

> 対応レクチャー：座学 `L1-3a`／実践 `L1-3b` ／ 対応スキル：S1.b-1,2,3,4
> 認証は**キーレス**（`az login` ＋ `DefaultAzureCredential`）。APIキーは使いません。

## ファイル構成
| ファイル | 役割 |
|---|---|
| `deploy_model.azcli` | **Azure CLI** で Foundry リソース＋プロジェクト＋モデルデプロイを作成（手順を1行ずつ実行） |
| `main.bicep` | **IaC（Bicep）**：同じ構成を宣言的にコード化（`accounts`／`accounts/projects`／`accounts/deployments`） |
| `deploy_bicep.azcli` | Bicep の `what-if`（変更プレビュー）→ `create`（適用）コマンド |
| `main.py` | デプロイの**スモークテスト**（キーレスで推論し、デプロイの健全性を確認） |
| `.env.sample` | `main.py` 用の環境変数雛形（`PROJECT_ENDPOINT` / `DEPLOYMENT_NAME`） |
| `requirements.txt` | Python 依存パッケージ |
| `eval/dataset.json` | 評価ゲート用のデータセット（評価器＋テストクエリ） |
| `github-workflow-sample/evaluate-and-deploy.yml` | **GitHub Actions 雛形**：PR で評価ゲート、main で評価→デプロイ |

## 前提
- Azure サブスクリプション ／ `az login` 済み ／ Azure CLI（`cognitiveservices` 拡張：`az extension add -n cognitiveservices`）
- `jq`（CLI 手順の整形に使用。未導入なら https://stedolan.github.io/jq/download/ ）
- Python 3.11+

## 進め方（どちらか or 両方）
**A. CLI で作る**
1. `deploy_model.azcli` の変数（RG/ACCOUNT/LOCATION 等）を自分の値に置換。
2. 上から1行ずつ実行（手順4の `list-models` でモデル名/バージョンを確認してから手順5を実行）。

**B. Bicep（IaC）で作る**
1. `deploy_bicep.azcli` の変数を置換し、`what-if` → `create` を実行。
2. 出力（`foundryEndpoint` / `deploymentNameOut`）を控える。

**共通: スモークテスト**
```bash
python -m venv .venv
. .venv/Scripts/activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env             # Windows: copy .env.sample .env
# .env に PROJECT_ENDPOINT と DEPLOYMENT_NAME を設定してから:
python main.py
```

**CI/CD 雛形（任意）**
- `github-workflow-sample/evaluate-and-deploy.yml` をリポジトリ直下 `.github/workflows/` にコピーし、OIDC（キーレス）と各リポジトリ変数を設定すると、PR で評価ゲート・main で評価→デプロイが動きます。

## 後片付け（課金回避）
作成したリソースグループを丸ごと削除します（デプロイ・リソースは課金対象）。
```bash
az group delete --name ai103-l1-3-rg
```

## 注意（揮発情報）
- **モデル名/バージョン・SKU・API バージョン**は変動します。`list-models` と公式ドキュメントで都度確認。
- `microsoft/ai-agent-evals` と `azd` の hosted agent CI/CD は**プレビュー**。
