from pathlib import Path
import requests
import os
import json
from playsound import playsound
from dotenv import load_dotenv
import helper_module
import settings

# Define chunk size for audio file
CHUNK_SIZE = 1024

# Eleven Labs only supports mp3, no wav support yet
load_dotenv()
headers = {
    "Accept": "audio/mp3",
    "Content-Type": "application/json",
    "xi-api-key": os.environ["XI_API_KEY"],
}

# Define settings for different characters
character_settings = {
    settings.VOICE_NAME_AI.lower(): (
        settings.VOICE_FILE_AI,
        settings.VOICE_URL_AI,
    ),
    settings.VOICE_NAME_HUMAN.lower(): (
        settings.VOICE_FILE_HUMAN,
        settings.VOICE_URL_HUMAN,
    ),
    settings.VOICE_NAME_SYSTEM.lower(): (
        settings.VOICE_FILE_SYSTEM,
        settings.VOICE_URL_SYSTEM,
    ),
}


def get_voices():
    # Define URL and headers
    url = settings.VOICES_URL
    my_headers = {"Accept": "application/json", "xi-api-key": os.environ["XI_API_KEY"]}
    response = requests.get(url, headers=my_headers)
    json_data = json.loads(response.text)
    for voice in json_data["voices"]:
        name = voice["name"]
        voice_id = voice["voice_id"]
        category = voice["category"]
        description = voice["description"]
        gender = voice["labels"].get("gender", "Unknown")
        age = voice["labels"].get("age", "Unknown")
        use_case = voice["labels"].get("use case", "Unknown")
        helper_module.log(
            f"{name}({voice_id}) - {category}({gender}-{age}-{use_case}) : {description}",
            "info",
        )


def generate_audio(
        text="No Text Given. Please give me some text to read.",
        character=settings.VOICE_NAME_AI,
):
    # Define data for POST request
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0,
            "use_speaker_boost": True,
        },
    }
    audio_file, url = character_settings.get(
        character.lower(), character_settings[character.lower()]
    )
    response = requests.post(url, json=data, headers=headers)
    p = Path(audio_file)
    with p.open("wb") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)


# playsound requires PyObjC on Mac: pip3 install PyObjC
def play_audio(audio_file=None):
    if audio_file is None:
        audio_file = settings.VOICE_FILE_SYSTEM
    if os.path.exists(audio_file):
        playsound(audio_file)
    else:
        helper_module.log(f"No such file:{audio_file}", "error")


if __name__ == "__main__":
    get_voices()
    generate_audio(character=settings.VOICE_NAME_SYSTEM.lower())
    generate_audio(character=settings.VOICE_NAME_HUMAN.lower())
    generate_audio(character=settings.VOICE_NAME_AI.lower())
    play_audio(settings.VOICE_FILE_SYSTEM)
    play_audio(settings.VOICE_FILE_HUMAN)
    play_audio(settings.VOICE_FILE_AI)
