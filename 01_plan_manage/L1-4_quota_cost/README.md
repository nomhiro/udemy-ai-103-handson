# L1-4 実践: クォータ確認 ＋ レート制限リトライ ＋ コストタグ

デプロイの **クォータ消費をプログラムで確認**し、**レート制限(429)に強いリトライ**を実装し、**コスト按分のタグ**を付けるハンズオンです。

> 対応レクチャー：座学 `L1-4-1`(クォータ)／`L1-4-2`(レート制限・スケーリング)／`L1-4-3`(コスト管理)、実践 `L1-4-4` ／ 対応スキル：S1.c-1
> 認証は**キーレス**（`az login` ＋ `DefaultAzureCredential`）。APIキーは使いません。

## ファイル構成
| ファイル | 役割 |
|---|---|
| `check_quota.py` | **ARM REST**（quotaTiers / Usages / Model Capacities API）でティア・クォータ消費・空き容量を確認 |
| `retry_demo.py` | **429 リトライ**：SDK 組み込み（`max_retries`）と手動の指数バックオフ＋ジッター |
| `tag_resources.azcli` | **コスト按分タグ**を RG／Foundry リソースに付与（Azure CLI） |
| `.env.sample` | 環境変数の雛形 |
| `requirements.txt` | Python 依存パッケージ |

## 前提
- Azure サブスクリプション ／ `az login` 済み ／ Python 3.11+
- ロール：クォータ閲覧は **Cognitive Services Usages Reader**（サブスクリプションスコープ）、タグ付与は対象リソースに **Contributor** 以上
- 比較対象のモデルが Foundry プロジェクトにデプロイ済み（`MODEL_DEPLOYMENT`）

## 進め方（PowerShell）
```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1     # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.sample .env            # macOS/Linux: cp .env.sample .env
# .env を編集してから:

python check_quota.py            # ティア / クォータ消費 / 空き容量を表示
python retry_demo.py             # SDK / 手動 両方のリトライで推論
# tag_resources.azcli は PowerShell 前提。変数を置換してから1行ずつ実行推奨
```

## 期待される出力（例）
`check_quota.py`：
```
===== クォータティア (このサブスクリプションの等級) =====
現在のティア: Tier 1
割り当て日   : 2025-10-18T05:09:05.6334222Z
昇格ポリシー : OnceUpgradeIsAvailable

===== クォータ消費 / 上限 (eastus) =====
Tokens Per Minute (thousands) - gpt-5.4: 0/150
...
```
`retry_demo.py`：通常は 429 なしで成功（`max_retries` 設定により、429 が出れば自動でバックオフ再試行）。

## つまずきポイント
| 症状 | 対処 |
|---|---|
| `check_quota.py` で 403 | サブスクスコープに **Cognitive Services Usages Reader** を付与 |
| `limit > 0` の行が出ない | `QUOTA_LOCATION`／サブスクが正しいか確認 |
| 使いたいモデルの行がそもそも無い／`insufficient quota` でデプロイできない | **クォータティア**が原因。最下位ティア（Free Tier / Tier 0）では `gpt-4.1-mini` / `gpt-5-mini` / `o4-mini` / `text-embedding-3-small` 以外は割り当てゼロ。`.env.sample` のフォールバック（`gpt-5-mini`）に読み替える。**リージョン変更では解決しない** → 詳細はリポジトリ直下の [`FAQ.md`](../../FAQ.md) |
| `model not found` | `MODEL_DEPLOYMENT` が**デプロイ名**と一致しているか（カタログ名でなくデプロイ名） |
| 429 が再現しない | 正常。クォータ超過時に自動再試行される形であることを確認する目的 |
| ティアが取得できない | `quotaTiers` はプレビュー API。取得できなくても後続の確認は続行される |

## 後片付け（課金回避）
- このハンズオンは**推論を数回**するだけ（数円程度）。`check_quota` と `tag` は基本無料。**新しくリソースは作りません**。
- 不要なら付与したタグを削除：`az tag delete --resource-id <id> --name project -y`
- ⚠️ タグを付けたリソースグループは他のレッスンでも使い回すので、**RG ごとの削除はしないでください**（削除するのは講座を終えるときだけ）。

## 注意（揮発情報）
- **ARM の api-version**（`2024-10-01`）、**capacity unit の RPM/TPM 比**、**SDK 既定リトライ回数**は変動。公式ドキュメントで都度確認。
- **project レベルのコスト按分はプレビュー**。RBAC ロールは改称中（Azure AI User → Foundry User）。
