import time
import os
import wave
import array
from config.logger import setup_logging
from typing import Optional, Tuple, List
from core.providers.asr.dto.dto import InterfaceType
from core.providers.asr.base import ASRProviderBase

import requests

TAG = __name__
logger = setup_logging()


def _normalize_audio(file_path: str, target_peak_pct: float = 85.0, max_gain: float = 30.0):
    """Hebt leise Aufnahmen digital auf einen Ziel-Pegel an, bevor sie an
    Whisper gehen (zusaetzlich zur Hardware-Mikrofonverstaerkung). Loggt
    Dauer/Pegel/angewandte Verstaerkung, damit sich Mikrofon- von echten
    ASR-Problemen unterscheiden lassen, ohne die Datei vom Geraet zu holen."""
    try:
        with wave.open(file_path, "rb") as wf:
            n_frames = wf.getnframes()
            framerate = wf.getframerate()
            sampwidth = wf.getsampwidth()
            n_channels = wf.getnchannels()
            raw = wf.readframes(n_frames)
        duration_s = n_frames / float(framerate) if framerate else 0

        if sampwidth != 2 or not raw:
            logger.bind(tag=TAG).info(
                f"Audio-Diagnose: Dauer={duration_s:.2f}s (Pegel-Analyse "
                f"uebersprungen, sampwidth={sampwidth})"
            )
            return

        samples = array.array("h")
        samples.frombytes(raw[: len(raw) - (len(raw) % 2)])
        if not samples:
            return

        peak = max(abs(s) for s in samples)
        rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
        peak_pct = round(100 * peak / 32768, 1)
        rms_pct = round(100 * rms / 32768, 1)

        gain = 1.0
        if peak > 0:
            target_peak = 32768 * (target_peak_pct / 100.0)
            gain = min(target_peak / peak, max_gain)

        if gain > 1.05:
            for i in range(len(samples)):
                v = int(samples[i] * gain)
                samples[i] = max(-32768, min(32767, v))
            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(n_channels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(framerate)
                wf.writeframes(samples.tobytes())

        logger.bind(tag=TAG).info(
            f"Audio-Diagnose: Dauer={duration_s:.2f}s, Peak={peak_pct}%, "
            f"RMS(durchschn. Lautstaerke)={rms_pct}%, "
            f"digitale Verstaerkung angewandt={round(gain, 1)}x"
        )
    except Exception as e:
        logger.bind(tag=TAG).warning(f"Audio-Normalisierung fehlgeschlagen: {e}")

class ASRProvider(ASRProviderBase):
    def __init__(self, config: dict, delete_audio_file: bool):
        self.interface_type = InterfaceType.NON_STREAM
        self.api_key = config.get("api_key")
        self.api_url = config.get("base_url")
        self.model = config.get("model_name")
        self.output_dir = config.get("output_dir")
        self.delete_audio_file = delete_audio_file
        # Sprache fest vorgeben statt vom Whisper-Endpoint autodetecten zu
        # lassen - bei kurzen/undeutlichen Clips rät die Autodetect sonst
        # gerne auf eine falsche Sprache (z.B. Italienisch statt Deutsch).
        self.language = config.get("language", "de")

        os.makedirs(self.output_dir, exist_ok=True)

    def requires_file(self) -> bool:
        return True

    async def speech_to_text(self, opus_data: List[bytes], session_id: str, artifacts=None) -> Tuple[Optional[str], Optional[str]]:
        file_path = None
        try:
            if artifacts is None:
                return "", None
            file_path = artifacts.file_path

            logger.bind(tag=TAG).info(f"file path: {file_path}")
            _normalize_audio(file_path)
            headers = {
                "Authorization": f"Bearer {self.api_key}",
            }

            # 使用data参数传递模型名称
            data = {
                "model": self.model
            }
            if self.language:
                data["language"] = self.language


            with open(file_path, "rb") as audio_file:  # 使用with语句确保文件关闭
                files = {
                    "file": audio_file
                }

                start_time = time.time()
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=headers
                )
                logger.bind(tag=TAG).debug(
                    f"语音识别耗时: {time.time() - start_time:.3f}s | 结果: {response.text}"
                )

            if response.status_code == 200:
                text = response.json().get("text", "")
                return text, file_path
            else:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")

        except Exception as e:
            logger.bind(tag=TAG).error(f"语音识别失败: {e}")
            return "", None
