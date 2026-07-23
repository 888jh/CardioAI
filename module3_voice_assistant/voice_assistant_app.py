"""
CardioAI - 心血管疾病智能辅助系统
Module 3: VoiceDoc - AI 驱动的心血管健康语音顾问

功能：
- DeepSeek LLM 专业健康问答
- CosyVoice TTS 语音合成
- Flask API 服务

执行方式：
    D:\software\anaconda3\envs\cardioenv\python.exe voice_assistant_app.py
    
访问地址：
    http://localhost:5001
"""

import os
import base64
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat
import dashscope

# ==================== 环境配置 ====================

# 加载环境变量
load_dotenv("D:/cursor_pro/pro1/.env")

# ===== 模拟模式配置 =====
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"  # 默认使用模拟数据

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY1")
DEEPSEEK_BASE_URL = os.getenv("base_url1", "https://api.deepseek.com").strip('"')

# DashScope 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
DASHSCOPE_BASE_URL = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1").strip('"')

print("=" * 60)
print("VoiceDoc - AI 心血管健康语音顾问")
print("=" * 60)
print()
print("[配置] 正在初始化...")
print(f"[模式] 模拟数据模式: {'启用' if USE_MOCK_DATA else '禁用'}")

# 验证配置
if not USE_MOCK_DATA:
    if not DEEPSEEK_API_KEY:
        print("[警告] DEEPSEEK_API_KEY1 未配置")
    if not DASHSCOPE_API_KEY:
        print("[警告] DASHSCOPE_API_KEY 未配置")
    
    if DEEPSEEK_API_KEY and DASHSCOPE_API_KEY:
        print("[OK] API Keys 加载成功")
        print(f"[OK] DASHSCOPE Base URL: {DASHSCOPE_BASE_URL}")
else:
    print("[OK] 模拟模式已启用，无需真实 API Keys")

# ==================== DeepSeek LLM 初始化 ====================

SYSTEM_PROMPT = """你是一位专业的心血管健康顾问，具备丰富的医学知识。
你的职责是：
1. 回答关于心血管疾病的问题
2. 提供健康建议和预防措施
3. 解释心血管相关的医学术语
4. 给出生活方式改善建议

请用专业但易懂的语言回答，每次回答控制在200字以内。
注意：你的建议仅供参考，不能替代专业医疗诊断。"""

llm = None
if not USE_MOCK_DATA:
    try:
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.7,
            max_tokens=500
        )
        print("[OK] DeepSeek LLM 初始化成功")
    except Exception as e:
        print(f"[错误] DeepSeek LLM 初始化失败: {str(e)}")
else:
    print("[OK] DeepSeek LLM 模拟模式")

# ==================== CosyVoice TTS 函数 ====================

def generate_mock_audio_with_tts(text: str) -> bytes:
    """
    使用系统 TTS 生成语音（pyttsx3）
    注意：此方法可能与 Flask 调试模式冲突
    """
    import tempfile
    import os
    import subprocess
    import time
    
    try:
        # 创建临时文件
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav', mode='w')
        temp_path = temp_file.name
        temp_file.close()
        
        # 创建独立的 Python 脚本来运行 TTS（避免 Flask 冲突）
        script_content = f'''
import pyttsx3
import sys

text = {repr(text)}
output_path = {repr(temp_path)}

try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    # 尝试设置中文语音
    for voice in voices:
        if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    engine.save_to_file(text, output_path)
    engine.runAndWait()
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {{e}}")
    sys.exit(1)
'''
        
        # 保存脚本到临时文件
        script_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py', mode='w', encoding='utf-8')
        script_file.write(script_content)
        script_file.close()
        
        # 执行脚本
        result = subprocess.run(
            [r'D:\software\anaconda3\envs\cardioenv\python.exe', script_file.name],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 删除脚本文件
        try:
            os.unlink(script_file.name)
        except:
            pass
        
        # 检查是否成功
        if result.returncode == 0 and 'SUCCESS' in result.stdout:
            # 等待文件写入完成
            time.sleep(0.5)
            
            # 读取音频文件
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                with open(temp_path, 'rb') as f:
                    audio_data = f.read()
                
                # 删除临时文件
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
                return audio_data
        
        raise Exception(f"TTS 执行失败: {result.stderr}")
        
    except Exception as e:
        print(f"[警告] TTS 失败: {str(e)}")
        raise


def generate_mock_audio(text: str) -> bytes:
    """
    生成模拟音频数据（朗读文本内容）
    优先使用 TTS，失败时使用音调
    
    参数：
        text: 要朗读的文本内容
    返回：
        WAV 格式的音频数据
    """
    import io
    import wave
    import struct
    import math
    
    # 尝试使用 TTS
    try:
        return generate_mock_audio_with_tts(text)
    except Exception as e:
        print(f"[警告] TTS 不可用: {str(e)}")
        print("[备用] 使用音调代替")
    
    # 备用方案：生成音调
    sample_rate = 22050
    duration = 1.0
    frequency = 440.0
    amplitude = 0.3
    
    num_samples = int(sample_rate * duration)
    samples = []
    
    for i in range(num_samples):
        sample = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
        sample_int = int(sample * 32767)
        samples.append(sample_int)
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for sample in samples:
            wav_file.writeframes(struct.pack('<h', sample))
    
    wav_data = wav_buffer.getvalue()
    wav_buffer.close()
    
    return wav_data


def text_to_speech(text: str) -> bytes:
    """
    将文字转换为语音（同步调用）
    
    参数：
        text: 待合成的文本（限制2000字符）
    返回：
        二进制音频数据（模拟模式: WAV格式 / 真实模式: MP3格式）
    """
    # 模拟模式：使用离线 TTS 朗读文本
    if USE_MOCK_DATA:
        print(f"[模拟] 使用离线 TTS 朗读文本（文本长度: {len(text)} 字符）")
        mock_audio = generate_mock_audio(text)
        print(f"[OK] 离线语音合成成功（WAV格式），大小: {len(mock_audio)} bytes")
        return mock_audio
    
    # 真实模式：调用 CosyVoice API
    try:
        # 文本长度限制
        if len(text) > 2000:
            text = text[:2000]
            print(f"[警告] 文本超过2000字符，已截断")
        
        # 初始化语音合成器（每次调用需重新初始化）
        synthesizer = SpeechSynthesizer(
            model='cosyvoice-v2',
            voice='longxiaochun_v2',
            format=AudioFormat.MP3_22050HZ_MONO_256KBPS
        )
        
        # 同步调用合成
        audio_data = synthesizer.call(text)
        
        if audio_data:
            print(f"[OK] 语音合成成功，音频大小: {len(audio_data)} bytes")
            return audio_data
        else:
            print("[错误] 语音合成返回空数据")
            return None
        
    except Exception as e:
        print(f"[错误] TTS 合成失败: {str(e)}")
        return None

# ==================== Flask 应用 ====================

app = Flask(__name__)

@app.route('/')
def home():
    """主页 - 渲染语音助手界面"""
    return render_template('voice_index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """
    AI 问答接口
    
    请求格式（JSON）:
    {
        "question": "什么是高血压？"
    }
    
    响应格式（JSON）:
    {
        "success": true,
        "text_answer": "高血压是指...",
        "audio_base64": "base64编码的MP3音频",
        "timestamp": "2026-07-23 19:00:00"
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '问题不能为空'
            }), 400
        
        print(f"\n[请求] 用户问题: {question}")
        
        # 获取 LLM 回答
        if USE_MOCK_DATA:
            # 模拟模式：返回预设回答
            print("[模拟] 使用模拟 LLM 回答")
            mock_answers = {
                "高血压": "高血压是指血压持续高于正常水平的状态。正常血压通常在120/80 mmHg以下。高血压可能导致心脏病、中风等严重并发症。建议：1)减少盐分摄入 2)保持健康体重 3)规律运动 4)戒烟限酒 5)定期监测血压。如有不适请及时就医。",
                "心脏病": "心脏病包括多种心血管疾病，如冠心病、心肌梗死等。常见症状包括胸痛、气短、心悸。预防措施：1)健康饮食（低脂、低盐）2)规律运动 3)控制体重 4)戒烟 5)管理压力 6)定期体检。若出现胸痛等症状，请立即就医。",
                "胆固醇": "胆固醇是血液中的一种脂质。总胆固醇应低于5.2 mmol/L，低密度脂蛋白（LDL，'坏'胆固醇）应低于3.4 mmol/L。高胆固醇可导致动脉硬化。改善方法：1)减少饱和脂肪摄入 2)增加纤维食物 3)适量运动 4)控制体重。必要时遵医嘱服用降脂药。",
                "default": f"感谢您咨询关于'{question}'的问题。作为心血管健康顾问，我建议您：1)保持健康的生活方式，包括均衡饮食和规律运动 2)定期监测血压、血糖和胆固醇水平 3)避免吸烟和过量饮酒 4)保持健康体重 5)管理压力。如有具体症状或疑虑，请及时咨询专业医生。记住，这些建议仅供参考，不能替代专业医疗诊断。"
            }
            
            # 根据问题关键词选择回答
            text_answer = mock_answers["default"]
            for keyword, answer in mock_answers.items():
                if keyword in question and keyword != "default":
                    text_answer = answer
                    break
        else:
            # 真实模式：调用 DeepSeek LLM
            print("[处理] 正在调用 DeepSeek LLM...")
            full_prompt = f"{SYSTEM_PROMPT}\n\n用户问题：{question}"
            response = llm.invoke(full_prompt)
            text_answer = response.content
        
        print(f"[OK] LLM 回答长度: {len(text_answer)} 字符")
        print(f"[回答] {text_answer[:100]}...")
        
        # 文字转语音
        print("[处理] 正在合成语音...")
        audio_data = text_to_speech(text_answer)
        
        if audio_data is None:
            return jsonify({
                'success': False,
                'error': '语音合成失败，请重试'
            }), 500
        
        # Base64 编码
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        print(f"[OK] Base64 编码完成，长度: {len(audio_base64)} 字符")
        
        # 返回结果
        result = {
            'success': True,
            'text_answer': text_answer,
            'audio_base64': audio_base64,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"[完成] 请求处理成功\n")
        
        return jsonify(result)
        
    except Exception as e:
        error_msg = f'处理失败: {str(e)}'
        print(f"[错误] {error_msg}")
        return jsonify({
            'success': False,
            'error': error_msg
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'mock_mode': USE_MOCK_DATA,
        'deepseek_configured': bool(DEEPSEEK_API_KEY) if not USE_MOCK_DATA else 'N/A (Mock Mode)',
        'dashscope_configured': bool(DASHSCOPE_API_KEY) if not USE_MOCK_DATA else 'N/A (Mock Mode)',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


# ==================== 应用启动 ====================

if __name__ == '__main__':
    print()
    print("[启动] Flask 应用启动中...")
    print("[地址] http://localhost:5001")
    print("[健康检查] http://localhost:5001/health")
    print()
    print("按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    # 启动 Flask 应用（端口5001，避免与Module 2冲突）
    # debug=False 以避免与 pyttsx3 的文件监控冲突
    app.run(debug=False, host='0.0.0.0', port=5001)
