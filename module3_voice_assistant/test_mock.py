"""
测试 Module 3 语音助手（模拟数据模式）

执行方式：
    D:\software\anaconda3\envs\cardioenv\python.exe test_mock.py
"""

import requests
import json
import base64

# 测试配置
API_URL = "http://localhost:5001/ask"
HEALTH_URL = "http://localhost:5001/health"

def test_health_check():
    """测试健康检查接口"""
    print("=" * 60)
    print("1. 测试健康检查接口")
    print("=" * 60)
    
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        result = response.json()
        
        print(f"[状态] {response.status_code}")
        print(f"[模式] Mock Mode: {result.get('mock_mode')}")
        print(f"[DeepSeek] {result.get('deepseek_configured')}")
        print(f"[DashScope] {result.get('dashscope_configured')}")
        print(f"[时间] {result.get('timestamp')}")
        print("[OK] 健康检查通过\n")
        return True
    except Exception as e:
        print(f"[错误] 健康检查失败: {str(e)}\n")
        return False


def test_ask_question(question):
    """测试问答接口"""
    print("=" * 60)
    print(f"2. 测试问答接口 - 问题: {question}")
    print("=" * 60)
    
    try:
        # 发送请求
        payload = {"question": question}
        response = requests.post(API_URL, json=payload, timeout=30)
        result = response.json()
        
        # 检查响应
        if result.get('success'):
            print(f"[OK] 请求成功")
            print(f"\n[文字回答]")
            print(f"{result.get('text_answer')}\n")
            
            # 检查音频数据
            audio_base64 = result.get('audio_base64', '')
            if audio_base64:
                audio_size = len(audio_base64)
                # 解码验证
                try:
                    audio_bytes = base64.b64decode(audio_base64)
                    print(f"[音频数据]")
                    print(f"  - Base64 长度: {audio_size} 字符")
                    print(f"  - 音频大小: {len(audio_bytes)} bytes")
                    print(f"  - 解码状态: 成功")
                    
                    # 可选：保存音频文件
                    # with open("test_audio.mp3", "wb") as f:
                    #     f.write(audio_bytes)
                    # print(f"  - 已保存: test_audio.mp3")
                    
                except Exception as e:
                    print(f"[警告] 音频解码失败: {str(e)}")
            else:
                print(f"[警告] 未收到音频数据")
            
            print(f"\n[时间戳] {result.get('timestamp')}")
            print("[OK] 测试通过\n")
            return True
        else:
            print(f"[错误] 请求失败: {result.get('error')}\n")
            return False
            
    except Exception as e:
        print(f"[错误] 测试失败: {str(e)}\n")
        return False


def main():
    """主测试函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "Module 3 模拟数据模式测试" + " " * 24 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 测试健康检查
    if not test_health_check():
        print("[失败] 请确保 Flask 应用正在运行")
        return
    
    # 测试问答（使用多个关键词）
    test_questions = [
        "什么是高血压？",
        "如何预防心脏病？",
        "胆固醇高了怎么办？"
    ]
    
    success_count = 0
    for question in test_questions:
        if test_ask_question(question):
            success_count += 1
    
    # 总结
    print("=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"[完成] 共测试 {len(test_questions)} 个问题")
    print(f"[成功] {success_count} 个")
    print(f"[失败] {len(test_questions) - success_count} 个")
    print()


if __name__ == "__main__":
    main()
