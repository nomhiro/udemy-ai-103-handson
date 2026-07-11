"""L3-2 実践: テキストから短い動画を非同期生成して取得する(Sora)。

動画生成は非同期。ライフサイクルは:
  1) ジョブ作成 (POST .../video/generations/jobs)
  2) 状態ポーリング (GET .../jobs/{id})  queued -> running -> succeeded
  3) 動画ダウンロード (GET .../generations/{id}/content/video) -> output.mp4

認証はキーレス (az login 済みの DefaultAzureCredential)。動画生成はプレビュー。
"""

import os
import time
import requests
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
deployment_name = os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"]

# 動画生成はプレビュー期間中、api-version は 'preview' を使う
api_version = "preview"

# --- キーレス認証(az login 済みの資格情報からトークンを取得) ---
credential = DefaultAzureCredential()
token = credential.get_token("https://ai.azure.com/.default")
headers = {"Authorization": f"Bearer {token.token}", "Content-Type": "application/json"}

try:
    # 1) ジョブ作成(テキスト -> 動画)。検証用に小さい解像度・短い秒数で
    create_url = f"{endpoint}/openai/v1/video/generations/jobs?api-version={api_version}"
    body = {
        "prompt": "A cat playing piano in a cozy jazz bar, warm lighting",
        "width": 480,
        "height": 480,
        "n_seconds": 5,
        "model": deployment_name,
    }
    response = requests.post(create_url, headers=headers, json=body)
    response.raise_for_status()
    job_id = response.json()["id"]
    print(f"Job created: {job_id}")

    # 2) 状態をポーリング(succeeded/failed/cancelled になるまで)
    status_url = f"{endpoint}/openai/v1/video/generations/jobs/{job_id}?api-version={api_version}"
    status = None
    while status not in ("succeeded", "failed", "cancelled"):
        time.sleep(5)  # 数秒おきに確認(生成は1〜5分程度)
        status_response = requests.get(status_url, headers=headers).json()
        status = status_response.get("status")
        print(f"Job status: {status}")

    # 3) 完成した動画をダウンロード
    if status == "succeeded":
        generations = status_response.get("generations", [])
        if not generations:
            raise Exception("No generations found in job result.")
        generation_id = generations[0]["id"]
        video_url = f"{endpoint}/openai/v1/video/generations/{generation_id}/content/video?api-version={api_version}"
        video_response = requests.get(video_url, headers=headers)
        video_response.raise_for_status()
        with open("output.mp4", "wb") as f:
            f.write(video_response.content)
        print('✅ Generated video saved as "output.mp4"')
    else:
        raise Exception(f"Job didn't succeed. Status: {status}")
except Exception as ex:
    print(f"エラー: {ex}")
