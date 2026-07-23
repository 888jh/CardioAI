"""
CardioAI - 心血管疾病智能辅助系统
Module 2: Flask API 后端

功能：
- 提供 Web 界面
- /predict_cardio API 接口进行心血管疾病风险预测

执行方式：
    D:\software\anaconda3\envs\cardioenv\python.exe app.py
    
访问地址：
    http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime

app = Flask(__name__)

# ==================== 全局配置 ====================
MODEL_PATH = 'cardio_predictor_model.pkl'
model = None

# ==================== 加载模型 ====================
def load_model():
    """加载训练好的模型"""
    global model
    
    if not os.path.exists(MODEL_PATH):
        print(f"[错误] 模型文件不存在 - {MODEL_PATH}")
        print(f"请先运行 train_and_save.py 训练模型")
        return False
    
    try:
        model = joblib.load(MODEL_PATH)
        file_size = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"[OK] 模型加载成功: {MODEL_PATH} ({file_size:.2f} MB)")
        return True
    except Exception as e:
        print(f"[错误] 模型加载失败: {str(e)}")
        return False

# ==================== 路由定义 ====================

@app.route('/')
def home():
    """主页 - 渲染预测表单"""
    if model is None:
        return """
        <html>
        <head><title>CardioAI - 错误</title></head>
        <body style="font-family: Arial; padding: 50px; text-align: center;">
            <h1 style="color: #e74c3c;">[错误] 模型未加载</h1>
            <p>请先运行 <code>train_and_save.py</code> 训练并保存模型。</p>
            <p>训练命令：</p>
            <pre style="background: #f4f4f4; padding: 10px; display: inline-block;">
D:\\software\\anaconda3\\envs\\cardioenv\\python.exe train_and_save.py
            </pre>
        </body>
        </html>
        """
    return render_template('index.html')


@app.route('/predict_cardio', methods=['POST'])
def predict_cardio():
    """
    心血管疾病风险预测 API
    
    输入格式（JSON）:
    {
        "age": 18393,        # 年龄（天数）
        "gender": 2,         # 性别 (1=女性, 2=男性)
        "height": 168,       # 身高（cm）
        "weight": 62,        # 体重（kg）
        "ap_hi": 110,        # 收缩压（mmHg）
        "ap_lo": 80,         # 舒张压（mmHg）
        "cholesterol": 1,    # 胆固醇 (1=正常, 2=高, 3=很高)
        "gluc": 1,           # 血糖 (1=正常, 2=高, 3=很高)
        "smoke": 0,          # 吸烟 (0=否, 1=是)
        "alco": 0,           # 饮酒 (0=否, 1=是)
        "active": 1          # 运动 (0=否, 1=是)
    }
    
    输出格式（JSON）:
    {
        "success": true,
        "prediction": 0,           # 0=无病, 1=有病
        "probability": 0.23,       # 患病概率 (0-1)
        "risk_level": "低风险",    # 风险等级
        "input_summary": {...},    # 输入数据摘要
        "timestamp": "2026-07-23 18:00:00"
    }
    """
    try:
        # 检查模型是否加载
        if model is None:
            return jsonify({
                'success': False,
                'error': '模型未加载，请先训练模型'
            }), 500
        
        # 获取输入数据
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据为空'
            }), 400
        
        # 验证必需字段
        required_fields = ['age', 'gender', 'height', 'weight', 'ap_hi', 
                          'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'缺少必需字段: {", ".join(missing_fields)}'
            }), 400
        
        # ==================== 特征工程 ====================
        # 与训练时保持一致
        
        # 年龄转换（天 -> 年）
        age_years = round(data['age'] / 365)
        
        # 计算 BMI
        bmi = data['weight'] / ((data['height'] / 100) ** 2)
        
        # 构建特征字典（顺序必须与训练时一致）
        features = {
            'age_years': age_years,
            'gender': data['gender'],
            'height': data['height'],
            'weight': data['weight'],
            'bmi': bmi,
            'ap_hi': data['ap_hi'],
            'ap_lo': data['ap_lo'],
            'cholesterol': data['cholesterol'],
            'gluc': data['gluc'],
            'smoke': data['smoke'],
            'alco': data['alco'],
            'active': data['active']
        }
        
        # 转换为 DataFrame
        input_df = pd.DataFrame([features])
        
        # ==================== 模型预测 ====================
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]  # 患病概率（类别1的概率）
        
        # 风险等级划分
        if probability > 0.7:
            risk_level = "高风险"
            risk_color = "#e74c3c"
        elif probability > 0.4:
            risk_level = "中风险"
            risk_color = "#f39c12"
        else:
            risk_level = "低风险"
            risk_color = "#27ae60"
        
        # ==================== 返回结果 ====================
        result = {
            'success': True,
            'prediction': int(prediction),
            'prediction_label': '有心血管疾病' if prediction == 1 else '无心血管疾病',
            'probability': float(probability),
            'probability_percent': f"{probability * 100:.2f}%",
            'risk_level': risk_level,
            'risk_color': risk_color,
            'input_summary': {
                '年龄': f"{age_years} 岁 ({data['age']} 天)",
                '性别': '女性' if data['gender'] == 1 else '男性',
                '身高': f"{data['height']} cm",
                '体重': f"{data['weight']} kg",
                'BMI': f"{bmi:.2f}",
                '收缩压': f"{data['ap_hi']} mmHg",
                '舒张压': f"{data['ap_lo']} mmHg",
                '胆固醇': ['正常', '高于正常', '远高于正常'][data['cholesterol'] - 1],
                '血糖': ['正常', '高于正常', '远高于正常'][data['gluc'] - 1],
                '吸烟': '是' if data['smoke'] == 1 else '否',
                '饮酒': '是' if data['alco'] == 1 else '否',
                '运动': '是' if data['active'] == 1 else '否'
            },
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 打印日志
        print(f"[{result['timestamp']}] 预测请求: {risk_level} ({probability:.2%})")
        
        return jsonify(result)
        
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': f'数据格式错误: {str(ve)}'
        }), 400
    
    except Exception as e:
        print(f"[错误] 预测错误: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'预测失败: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'model_path': MODEL_PATH,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })


@app.route('/api/info', methods=['GET'])
def api_info():
    """API 信息接口"""
    return jsonify({
        'name': 'CardioAI - 心血管疾病预测 API',
        'version': '1.0',
        'endpoints': {
            '/': 'GET - 主页（预测表单）',
            '/predict_cardio': 'POST - 心血管疾病风险预测',
            '/health': 'GET - 健康检查',
            '/api/info': 'GET - API 信息'
        },
        'model_info': {
            'loaded': model is not None,
            'path': MODEL_PATH,
            'exists': os.path.exists(MODEL_PATH)
        }
    })


# ==================== 应用启动 ====================
if __name__ == '__main__':
    print("=" * 60)
    print("CardioAI - 心血管疾病预测系统 (Flask API)")
    print("=" * 60)
    print()
    
    # 加载模型
    if load_model():
        print()
        print("[启动] Flask 应用启动中...")
        print("[地址] http://localhost:5000")
        print("[文档] http://localhost:5000/api/info")
        print("[健康] http://localhost:5000/health")
        print()
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        print()
        
        # 启动 Flask 应用
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print()
        print("[错误] 无法启动应用：模型文件不存在")
        print("请先运行以下命令训练模型：")
        print()
        print("  D:\\software\\anaconda3\\envs\\cardioenv\\python.exe train_and_save.py")
        print()
