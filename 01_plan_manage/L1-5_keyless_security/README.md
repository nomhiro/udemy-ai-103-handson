# L1-5 実践: キーレス化（DefaultAzureCredential ＋ ロール割り当て）

**APIキーを使わず**、Microsoft Entra ID（`az login`／マネージドID）のトークンで Foundry を呼び、
**ロール割り当て**と **local auth 無効化（`disableLocalAuth`）** までやってキーレスを仕上げるハンズオンです。

> 対応レクチャー：座学 `L1-5-1`(キーレス・マネージドID)／`L1-5-2`(RBAC・Key Vault)／`L1-5-3`(ネットワーク分離)、実践 `L1-5-4` ／ 対応スキル：S1.c-4
> 認証は**キーレス**（`az login` ＋ `DefaultAzureCredential`）。APIキーは使いません。

## ファイル構成
| ファイル | 役割 |
|---|---|
| `main.py` | **Foundry プロジェクト**を `AIProjectClient` + `DefaultAzureCredential` でキーレス呼び出し（Responses API） |
| `keyless_openai_direct.py` | **OpenAI SDK + トークンプロバイダー**でモデル直接呼び出し。キー方式との対比 |
| `assign_role_disable_key.azcli` | **ロール割り当て**（Foundry User / Cognitive Services User）＋ **local auth 無効化** |
| `.env.sample` | 環境変数の雛形 |
| `requirements.txt` | Python 依存パッケージ |

## 前提
- Azure サブスクリプション ／ `az login` 済み ／ Python 3.11+
- Foundry プロジェクト作成済み・チャットモデルを1つデプロイ済み（例 `gpt-4.1`）
- ロール割り当て・`disableLocalAuth` 操作には **Owner / User Access Administrator** 等の権限

## 進め方
```bash
python -m venv .venv
. .venv/Scripts/activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.sample .env             # Windows: copy .env.sample .env
# .env を編集してから:

# 1) まずロールを割り当てる（assign_role_disable_key.azcli の 1)〜3) を実行）
# 2) キーレスで呼べることを確認
python main.py
python keyless_openai_direct.py
# 3) local auth を無効化（azcli の 4)）してキー方式が 401 になることを確認
```

## 期待される出力（例）
`main.py`：
```
✅ キーレスで接続: https://xxx.services.ai.azure.com/api/projects/yyy
----- モデル応答 -----
キーレス認証は、鍵を共有せず ID にロールを割り当てて最小権限で安全にアクセスできる点が利点です。
```

## つまずき
- `403 Forbidden`: ロール未割り当て。`main.py` はプロジェクトに **Foundry User**、`keyless_openai_direct.py` は Foundry リソースに **Cognitive Services User**。
- `401 Unauthorized`: `az login` 未実施／トークンスコープ違い。`disableLocalAuth` 後にキー方式を使うと 401（期待どおり）。
- ロール改称中のため、CLI では **Foundry User を GUID `53ca6127-...` で指定**。
