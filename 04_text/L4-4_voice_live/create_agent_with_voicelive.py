"""L4-4 実践: Voice Live 設定つき Foundry エージェントを作成する。

エージェントの metadata に Voice Live 設定（声・VAD・ノイズ抑制）を持たせる。
Voice Live 設定は metadata の 512字制限に合わせて分割格納する。キーレス認証。
"""

import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()


def chunk_config(config_json: str, limit: int = 512) -> dict:
    """Voice Live 設定を 512字制限に合わせて metadata へ分割格納。"""
    metadata = {"microsoft.voice-live.configuration": config_json[:limit]}
    remaining, n = config_json[limit:], 1
    while remaining:
        metadata[f"microsoft.voice-live.configuration.{n}"] = remaining[:limit]
        remaining, n = remaining[limit:], n + 1
    return metadata


def main():
    project = AIProjectClient(
        endpoint=os.environ["PROJECT_ENDPOINT"],
        credential=DefaultAzureCredential(),
    )

    # Voice Live セッション設定（声・VAD・ノイズ抑制）
    voice_live_config = {
        "session": {
            "voice": {"name": "en-US-Ava:DragonHDLatestNeural", "type": "azure-standard", "temperature": 0.8},
            "input_audio_transcription": {"model": "azure-speech"},
            "turn_detection": {
                "type": "azure_semantic_vad",
                "end_of_utterance_detection": {"model": "semantic_detection_v1_multilingual"},
            },
            "input_audio_noise_reduction": {"type": "azure_deep_noise_suppression"},
            "input_audio_echo_cancellation": {"type": "server_echo_cancellation"},
        }
    }

    agent = project.agents.create_version(
        agent_name=os.environ["AGENT_NAME"],
        definition=PromptAgentDefinition(
            model=os.environ["MODEL_DEPLOYMENT_NAME"],
            instructions="あなたは親切な日本語アシスタントです。簡潔に話してください。",
        ),
        metadata=chunk_config(json.dumps(voice_live_config)),
    )
    print(f"Agent created: {agent.name} (version {agent.version})")


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(f"[エラー] {ex}")
