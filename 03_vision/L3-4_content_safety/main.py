"""L3-4 実践: 画像を Content Safety に送り、しきい値で受理/拒否を判定する。

Content Safety は 4カテゴリ(Hate/Sexual/Violence/Self-Harm)の重大度(0/2/4/6)を
マルチラベルで返すだけ。受理(Accepted)/拒否(Rejected)はアプリ側がしきい値で決める。
認証はキーレス(DefaultAzureCredential)。
"""

import os
from azure.identity import DefaultAzureCredential
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import AnalyzeImageOptions, ImageData
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv

load_dotenv()

ENDPOINT = os.environ["CONTENT_SAFETY_ENDPOINT"]
IMAGE_PATH = "test.jpg"

# カテゴリごとの拒否しきい値(この重大度「以上」なら拒否)。0/2/4/6 の4段階。
# 例: 性的・暴力は厳しめ(2)、ヘイト・自傷は中(4)
THRESHOLDS = {"Sexual": 2, "Violence": 2, "Hate": 4, "SelfHarm": 4}

# キーレス認証
client = ContentSafetyClient(ENDPOINT, DefaultAzureCredential())


def analyze(image_path: str):
    with open(image_path, "rb") as f:
        request = AnalyzeImageOptions(image=ImageData(content=f.read()))
    response = client.analyze_image(request)

    rejected = False
    print("=== カテゴリ別の重大度 (0=Safe,2=Low,4=Medium,6=High) ===")
    for item in response.categories_analysis:
        cat = item.category
        sev = item.severity
        limit = THRESHOLDS.get(str(cat), 4)
        flag = "NG(拒否)" if sev >= limit else "OK"
        if sev >= limit:
            rejected = True
        print(f"  {cat}: severity={sev} / しきい値={limit} -> {flag}")

    verdict = "Rejected(拒否)" if rejected else "Accepted(受理)"
    print(f"\n判定: {verdict}")
    return verdict


if __name__ == "__main__":
    try:
        analyze(IMAGE_PATH)
    except HttpResponseError as ex:
        # リージョン未対応・権限不足・サイズ超過などはここに来る
        print(f"Content Safety エラー: {ex}")
    except Exception as ex:
        print(f"エラー: {ex}")
