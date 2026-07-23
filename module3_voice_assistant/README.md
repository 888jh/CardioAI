# Module 3: VoiceDoc - AI 心血管健康语音顾问

## 功能概述

Module 3 是 CardioAI 系统的 AI 语音助手模块，集成了 DeepSeek LLM 和 CosyVoice TTS，提供专业的心血管健康问答和语音播报功能。

### 核心功能

✅ **DeepSeek LLM 问答**
- 专业心血管健康顾问角色
- 智能回答健康相关问题
- 提供预防措施和生活建议
- 回答控制在 200 字以内

✅ **CosyVoice 语音合成**
- 文字转语音（TTS）
- 女声播报（longxiaochun_v2）
- MP3 格式，22.05kHz 采样率
- 同步调用，快速响应

✅ **Web 交互界面**
- 美观的渐变设计
- 实时问答交互
- 自动播放语音
- 示例问题快速填充

## 文件结构

```
module3_voice_assistant/
├── voice_assistant_app.py     # Flask 后端应用
├── templates/
│   └── voice_index.html       # 前端交互界面
└── README.md                  # 本文件
```

## 技术架构

### 1. DeepSeek LLM

**配置**：
- 模型：`deepseek-chat`
- Temperature: 0.7
- Max tokens: 500
- Base URL: https://api.deepseek.com

**System Prompt**：
```
你是一位专业的心血管健康顾问，具备丰富的医学知识。
- 回答关于心血管疾病的问题
- 提供健康建议和预防措施
- 解释心血管相关的医学术语
- 给出生活方式改善建议
```

### 2. CosyVoice TTS

**配置**：
- 模型：`cosyvoice-v2`
- 音色：`longxiaochun_v2`（女声）
- 格式：`AudioFormat.MP3_22050HZ_MONO_256KBPS`
- 调用方式：同步调用（`SpeechSynthesizer.call`）

### 3. 数据流程

```
用户输入问题
    ↓
Flask 接收请求
    ↓
构建完整 Prompt（System + User）
    ↓
DeepSeek LLM 生成文字答案
    ↓
CosyVoice 合成语音
    ↓
Base64 编码音频
    ↓
返回 JSON（文字 + 音频）
    ↓
前端展示文字并播放语音
```

## 环境配置

### API Keys 配置

在 `.env` 文件中配置以下环境变量：

```bash
# ===== 模拟数据模式 =====
# 设置为 true 启用模拟数据（用于测试），设置为 false 使用真实 API
USE_MOCK_DATA=true

# ===== DeepSeek API（注意变量名有后缀1）=====
DEEPSEEK_API_KEY1=sk-xxxxxxxxxxxxxxxx
base_url1="https://api.deepseek.com"

# ===== DashScope API（CosyVoice）=====
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxx
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 模拟数据模式

为了便于测试和开发，系统支持模拟数据模式：

**启用模拟模式**：
```bash
USE_MOCK_DATA=true  # 在 .env 文件中设置
```

**模拟模式特性**：
- ✅ 无需真实 API Keys（可用于离线测试）
- ✅ DeepSeek LLM 使用预设回答（支持高血压、心脏病、胆固醇等关键词）
- ✅ CosyVoice TTS 返回模拟音频数据
- ✅ 完整的数据流程测试（前端到后端）
- ✅ 适用于网络受限或 API 连接问题的环境

**切换到真实模式**：
```bash
USE_MOCK_DATA=false  # 在 .env 文件中设置
```
然后确保 `DEEPSEEK_API_KEY1` 和 `DASHSCOPE_API_KEY` 已正确配置。

**重要提示**：
- `DEEPSEEK_API_KEY1` 有后缀 `1`
- `base_url1` 有引号，代码会自动 strip
- 请替换为您自己的 API Key

### 依赖包

确保已安装（requirements.txt 已包含）：
- `Flask`
- `python-dotenv`
- `langchain-openai`
- `dashscope`

## 使用指南

### 启动应用

```bash
# 1. 激活环境
conda activate cardioenv

# 2. 进入目录
cd D:\cursor_pro\pro1\module3_voice_assistant

# 3. 启动应用
D:\software\anaconda3\envs\cardioenv\python.exe voice_assistant_app.py
```

**应用信息**：
- 运行端口：http://localhost:5001
- 健康检查：http://localhost:5001/health

### 访问界面

在浏览器打开：**http://localhost:5001**

### 使用步骤

1. 在输入框中输入您的问题
2. 点击"提问并获取语音回答"按钮
3. 等待 AI 处理（2-5 秒）
4. 查看文字答案
5. 自动播放语音回答

### 快捷操作

- **示例问题**：点击示例问题快速填充
- **快捷键**：`Ctrl + Enter` 提交问题
- **音频控制**：使用播放器控制条调节音量、暂停等

## API 接口文档

### 1. 主页

**端点**: `/`  
**方法**: `GET`  
**返回**: HTML 页面

### 2. 问答接口

**端点**: `/ask`  
**方法**: `POST`  
**Content-Type**: `application/json`

**请求格式**:
```json
{
  "question": "什么是高血压？如何预防？"
}
```

**响应格式**（成功）:
```json
{
  "success": true,
  "text_answer": "高血压是指动脉血压持续高于正常值的一种慢性疾病...",
  "audio_base64": "base64编码的MP3音频数据",
  "timestamp": "2026-07-23 19:00:00"
}
```

**响应格式**（失败）:
```json
{
  "success": false,
  "error": "错误信息"
}
```

### 3. 健康检查

**端点**: `/health`  
**方法**: `GET`

**响应**:
```json
{
  "status": "healthy",
  "deepseek_configured": true,
  "dashscope_configured": true,
  "timestamp": "2026-07-23 19:00:00"
}
```

## 示例问题

### 疾病相关
- "什么是高血压？如何预防？"
- "心血管疾病的主要症状有哪些？"
- "冠心病和心肌梗死有什么区别？"

### 健康建议
- "日常生活中如何保护心脏健康？"
- "哪些食物对心血管有益？"
- "运动对预防心血管疾病有什么帮助？"

### 风险因素
- "BMI 超标会增加心血管疾病风险吗？"
- "吸烟对心血管有什么影响？"
- "高胆固醇会导致什么问题？"

## 性能指标

### 响应时间

| 步骤 | 预计耗时 |
|-----|---------|
| DeepSeek LLM 响应 | 1-3 秒 |
| CosyVoice TTS 合成 | 1-2 秒 |
| Base64 编码 | <0.1 秒 |
| **总计** | **2-5 秒** |

### 限制说明

1. **文本长度**
   - LLM 回答：最多 200 字（通过 prompt 控制）
   - TTS 合成：最多 2000 字符

2. **API 调用**
   - DeepSeek：按 token 计费
   - CosyVoice：按字符计费（2 元/万字符）

## 技术要点

### 1. 环境变量处理

```python
# 注意变量名后缀和引号处理
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY1")
DEEPSEEK_BASE_URL = os.getenv("base_url1", "https://api.deepseek.com").strip('"')
```

### 2. TTS 同步调用

```python
# 每次调用需重新初始化
synthesizer = SpeechSynthesizer(
    model='cosyvoice-v2',
    voice='longxiaochun_v2',
    format=AudioFormat.MP3_22050HZ_MONO_256KBPS
)

# 同步调用
audio_data = synthesizer.call(text)
```

### 3. Base64 编码

```python
# 编码音频数据
audio_base64 = base64.b64encode(audio_data).decode('utf-8')
```

### 4. 前端音频播放

```javascript
// 构造 Data URL
const audioUrl = `data:audio/mp3;base64,${result.audio_base64}`;

// 设置并播放
audioPlayer.src = audioUrl;
await audioPlayer.play();
```

## 错误处理

### 常见错误

1. **API Key 未配置**
   - 检查 .env 文件
   - 确认变量名正确（注意后缀1）

2. **LLM 调用失败**
   - 检查网络连接
   - 验证 API Key 有效性
   - 查看 DeepSeek API 余额

3. **TTS 合成失败**
   - 检查 DASHSCOPE_API_KEY
   - 确认文本长度 <2000 字符
   - 查看 DashScope 余额

4. **音频播放失败**
   - 浏览器可能阻止自动播放
   - 手动点击播放按钮
   - 检查浏览器是否支持 MP3

## 注意事项

⚠️ **重要提示**：

1. **医疗免责声明**
   - 本系统仅供参考学习
   - 不能替代专业医疗诊断
   - 如有健康问题请咨询医生

2. **API 费用**
   - DeepSeek 和 CosyVoice 都是付费服务
   - 注意控制使用量
   - 建议设置费用预警

3. **数据安全**
   - API Key 不要提交到版本控制
   - 不要在前端暴露敏感信息
   - 建议使用 HTTPS 部署

4. **性能优化**
   - 考虑缓存常见问题的答案
   - 实现答案和音频缓存
   - 异步调用提升响应速度

## 测试示例

### 使用 curl 测试 API

```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是高血压？"}'
```

### Python 测试脚本

```python
import requests
import base64

# 发送请求
response = requests.post(
    'http://localhost:5001/ask',
    json={'question': '什么是高血压？'}
)

result = response.json()

if result['success']:
    print("文字答案:", result['text_answer'])
    
    # 保存音频
    audio_data = base64.b64decode(result['audio_base64'])
    with open('answer.mp3', 'wb') as f:
        f.write(audio_data)
    print("音频已保存到 answer.mp3")
```

## 未来改进

可选的功能增强：

- [ ] 实现问答历史记录
- [ ] 支持多轮对话上下文
- [ ] 添加音色选择功能
- [ ] 实现答案缓存机制
- [ ] 支持语音输入识别
- [ ] 添加用户反馈系统
- [ ] 多语言支持
- [ ] 移动端适配

## 故障排查

### 问题：应用无法启动

1. 检查 Python 环境：`conda activate cardioenv`
2. 检查依赖包：`pip list | grep -E "Flask|dashscope|langchain"`
3. 查看错误日志

### 问题：API 调用失败

1. 测试健康检查：`curl http://localhost:5001/health`
2. 检查环境变量：确认 .env 文件路径和内容
3. 验证 API Key：确保有效且有余额

### 问题：语音播放无声音

1. 检查浏览器音量设置
2. 查看浏览器控制台错误
3. 测试其他音频文件是否能播放
4. 尝试不同浏览器

## 联系方式

如有问题或建议，请联系开发团队。

---

**CardioAI - 心血管疾病智能辅助系统**  
Module 3: VoiceDoc AI 语音顾问 v1.0
