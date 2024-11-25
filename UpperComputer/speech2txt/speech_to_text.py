import os
import pyaudio
import wave
import requests
import json
import base64
import time
from utils import LOG


class SpeechToText:
    def __init__(self, api_key, secret_key):
        """
        初始化 SpeechToText 类，配置百度 API 的密钥和录音参数。
        """
        self.API_KEY = api_key
        self.SECRET_KEY = secret_key
        self.FORMAT = pyaudio.paInt16  # 16-bit resolution
        self.CHANNELS = 1             # 单声道
        self.RATE = 16000             # 16kHz 采样率
        self.CHUNK = 1024             # 帧大小
        self.WAVE_OUTPUT_FILENAME = "recorded_audio.wav"  # 默认音频文件名
        self.access_token = None      # 缓存 Access Token
        self.token_expiry = 0         # Access Token 的过期时间戳

    def get_access_token(self):
        """
        获取百度 API 的 Access Token，支持缓存。
        """
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token

        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": self.API_KEY,
            "client_secret": self.SECRET_KEY
        }
        response = requests.post(url, params=params)
        if response.status_code == 200:
            result = response.json()
            self.access_token = result.get("access_token")
            expires_in = result.get("expires_in", 0)  # 有效期（秒）
            self.token_expiry = time.time() + expires_in - 60  # 提前 60 秒刷新
            if self.access_token:
                return self.access_token
            else:
                raise Exception("Failed to retrieve access token: No token in response.")
        else:
            raise Exception(f"Failed to retrieve access token: {response.text}")


    def record_audio(self):
        """
        使用麦克风录音并保存为 WAV 文件。录音持续固定时长（例如 2 秒）。
        """
        RECORD_DURATION = 20  # 固定录音时长（秒）

        print(f"Recording for {RECORD_DURATION} seconds...")

        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True,
                        frames_per_buffer=self.CHUNK)

        frames = []
        start_time = time.time()

        try:
            while time.time() - start_time < RECORD_DURATION:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                frames.append(data)
                elapsed_time = time.time() - start_time
                print(f"Recording... {elapsed_time:.1f}/{RECORD_DURATION} seconds", end="\r")  # 实时显示录音时间
        except Exception as e:
            LOG.error(f"Error during recording: {e}")
        finally:
            LOG.info("\nRecording stopped.")
            stream.stop_stream()
            stream.close()
            p.terminate()

        # 保存录音数据到文件
        with wave.open(self.WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(p.get_sample_size(self.FORMAT))
            wf.setframerate(self.RATE)
            wf.writeframes(b''.join(frames))

        LOG.info(f"Audio saved to {self.WAVE_OUTPUT_FILENAME}")
        return self.WAVE_OUTPUT_FILENAME

    def recognize_speech(self, file_path=None, audio_data=None):
        """
        调用百度语音识别 API，将音频文件或二进制数据转化为文字。
        """
        if not file_path and not audio_data:
            raise ValueError("Either file_path or audio_data must be provided.")

        if file_path:
            with open(file_path, "rb") as f:
                audio_data = f.read()

        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        audio_length = len(audio_data)

        # 构造请求体
        url = "https://vop.baidu.com/server_api"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "token": self.get_access_token(),
            "cuid": "Python-SpeechToText",
            "speech": audio_base64,
            "len": audio_length
        })

        response = requests.post(url, headers=headers, data=payload)
        LOG.debug(f"Request payload: {payload}")  # 调试请求
        LOG.debug(f"Response: {response.text}")   # 调试响应

        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"][0]
            else:
                raise Exception(f"Speech recognition failed: {result.get('err_msg', 'Unknown error')}")
        else:
            raise Exception(f"Speech recognition API error: {response.text}")



