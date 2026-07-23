"""
简单测试脚本 - 测试语音朗读功能
"""

import requests
import json
import time

API_URL = "http://localhost:5001/ask"

print("=" * 60)
print("测试语音朗读功能")
print("=" * 60)
print()

question = "什么是高血压？"
print(f"问题: {question}")
print("正在发送请求...")
print()

try:
    start_time = time.time()
    response = requests.post(API_URL, json={"question": question}, timeout=60)
    elapsed_time = time.time() - start_time
    
    if response.status_code == 200:
        result = response.json()
        
        if result.get('success'):
            print(f"[OK] 请求成功")
            print(f"[OK] 响应时间: {elapsed_time:.2f} 秒")
            print()
            print(f"文字回答:")
            print(result['text_answer'])
            print()
            print(f"音频信息:")
            audio_b64 = result.get('audio_base64', '')
            print(f"  - Base64 长度: {len(audio_b64)} 字符")
            
            import base64
            audio_bytes = base64.b64decode(audio_b64)
            print(f"  - 音频大小: {len(audio_bytes)} bytes")
            print(f"  - 音频格式: WAV")
            print()
            print("[OK] 测试通过！")
        else:
            print(f"[错误] {result.get('error')}")
    else:
        print(f"[错误] HTTP 错误: {response.status_code}")
        
except Exception as e:
    print(f"[错误] 测试失败: {str(e)}")

print()
print("=" * 60)
