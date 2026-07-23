# Module 2: TabularFlow - 心血管风险预测模型

## 功能概述

Module 2 是 CardioAI 系统的机器学习预测模块，提供基于 XGBoost 的心血管疾病风险评估功能。

### 核心功能

✅ **模型训练**
- 数据加载与清洗（与 Module 1 一致）
- 特征工程（age_years, BMI 计算）
- Pipeline 封装（StandardScaler + OneHotEncoder + XGBoost）
- 交叉验证评估
- 模型持久化保存

✅ **Flask API 服务**
- RESTful API 接口
- JSON 格式输入输出
- 实时预测响应
- 健康检查接口

✅ **Web 交互界面**
- 美观的响应式设计
- 11 个输入字段表单
- 实时预测结果展示
- 风险等级可视化

## 文件结构

```
module2_predictor/
├── train_and_save.py          # 模型训练脚本（一次性执行）
├── cardio_predictor_model.pkl # 训练好的模型文件（执行训练后生成）
├── app.py                     # Flask 后端应用
├── templates/
│   └── index.html             # 前端表单页面
└── README.md                  # 本文件
```

## 使用指南

### 步骤 1: 训练模型

**首次使用前必须先训练模型！**

```bash
# 激活环境
conda activate cardioenv

# 进入目录
cd D:\cursor_pro\pro1\module2_predictor

# 训练模型
D:\software\anaconda3\envs\cardioenv\python.exe train_and_save.py
```

**训练过程**：
- ⏱️ 预计耗时：10-30 秒（取决于硬件）
- 📊 数据规模：约 60,000 条（清洗后）
- 💾 模型大小：约 1-2 MB
- 📈 预期准确率：70-75%

**训练输出示例**：
```
========================================
CardioAI - 心血管疾病预测模型训练
========================================

[1/6] 加载数据...
  ✓ 成功加载 70,000 条原始数据

[2/6] 特征工程...
  ✓ 年龄转换完成 (天数 -> 年龄)
  ✓ BMI 计算完成

[3/6] 数据清洗...
  ✓ 清洗完成
    - 保留数据: 62,812 条
    - 删除数据: 7,188 条 (10.27%)

[4/6] 特征选择...
  ✓ 特征数量: 12
  ✓ 目标分布: 无病=31,234 (49.7%), 有病=31,578 (50.3%)

[5/6] 构建 Pipeline...
  ✓ Pipeline 构建完成

[6/6] 训练模型...
  ✓ 训练完成 (耗时 5.23 秒)

  📊 模型评估:
    - 训练集准确率: 0.7456 (74.56%)
    - 测试集准确率: 0.7311 (73.11%)
    - 交叉验证准确率: 0.7298 (±0.0045)

✅ 模型训练完成！
```

### 步骤 2: 启动 Flask 应用

```bash
# 确保在 module2_predictor 目录下
cd D:\cursor_pro\pro1\module2_predictor

# 启动 Flask
D:\software\anaconda3\envs\cardioenv\python.exe app.py
```

**应用启动输出**：
```
========================================
CardioAI - 心血管疾病预测系统 (Flask API)
========================================

✅ 模型加载成功: cardio_predictor_model.pkl (1.23 MB)

🚀 启动 Flask 应用...
📍 访问地址: http://localhost:5000
📍 API 文档: http://localhost:5000/api/info
📍 健康检查: http://localhost:5000/health

按 Ctrl+C 停止服务器
========================================

 * Running on http://0.0.0.0:5000
```

### 步骤 3: 使用 Web 界面

在浏览器中打开：**http://localhost:5000**

填写 11 个健康指标：
1. 年龄（天数）
2. 性别
3. 身高（cm）
4. 体重（kg）
5. 收缩压（mmHg）
6. 舒张压（mmHg）
7. 胆固醇水平
8. 血糖水平
9. 是否吸烟
10. 是否饮酒
11. 是否运动

点击"开始预测"按钮，即可获得心血管疾病风险评估结果。

## API 接口文档

### 1. 预测接口

**端点**: `/predict_cardio`  
**方法**: `POST`  
**Content-Type**: `application/json`

**请求格式**:
```json
{
  "age": 18393,
  "gender": 2,
  "height": 168,
  "weight": 62,
  "ap_hi": 110,
  "ap_lo": 80,
  "cholesterol": 1,
  "gluc": 1,
  "smoke": 0,
  "alco": 0,
  "active": 1
}
```

**响应格式**:
```json
{
  "success": true,
  "prediction": 0,
  "prediction_label": "无心血管疾病",
  "probability": 0.2345,
  "probability_percent": "23.45%",
  "risk_level": "低风险",
  "risk_color": "#27ae60",
  "input_summary": {
    "年龄": "50 岁 (18393 天)",
    "性别": "男性",
    "身高": "168 cm",
    "体重": "62 kg",
    "BMI": "21.97",
    "收缩压": "110 mmHg",
    "舒张压": "80 mmHg",
    "胆固醇": "正常",
    "血糖": "正常",
    "吸烟": "否",
    "饮酒": "否",
    "运动": "是"
  },
  "timestamp": "2026-07-23 18:00:00"
}
```

**字段说明**:
- `prediction`: 0（无病）或 1（有病）
- `probability`: 患病概率（0-1）
- `risk_level`: 低风险（<0.4）、中风险（0.4-0.7）、高风险（>0.7）

### 2. 健康检查接口

**端点**: `/health`  
**方法**: `GET`

**响应**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_path": "cardio_predictor_model.pkl",
  "timestamp": "2026-07-23 18:00:00"
}
```

### 3. API 信息接口

**端点**: `/api/info`  
**方法**: `GET`

返回所有可用接口的详细信息。

## 输入字段说明

| 字段 | 说明 | 类型 | 范围/选项 | 示例 |
|-----|------|------|----------|------|
| age | 年龄 | 整数 | 天数 | 18393（约50岁）|
| gender | 性别 | 整数 | 1=女性, 2=男性 | 2 |
| height | 身高 | 整数 | cm | 168 |
| weight | 体重 | 整数 | kg | 62 |
| ap_hi | 收缩压 | 整数 | mmHg | 110 |
| ap_lo | 舒张压 | 整数 | mmHg | 80 |
| cholesterol | 胆固醇 | 整数 | 1=正常, 2=高, 3=很高 | 1 |
| gluc | 血糖 | 整数 | 1=正常, 2=高, 3=很高 | 1 |
| smoke | 吸烟 | 整数 | 0=否, 1=是 | 0 |
| alco | 饮酒 | 整数 | 0=否, 1=是 | 0 |
| active | 运动 | 整数 | 0=否, 1=是 | 1 |

## 技术架构

### 模型 Pipeline

```
输入数据
    ↓
ColumnTransformer
    ├─ StandardScaler (连续特征)
    │   └─ age_years, height, weight, bmi, ap_hi, ap_lo
    └─ OneHotEncoder (分类特征)
        └─ gender, cholesterol, gluc, smoke, alco, active
    ↓
XGBClassifier
    ├─ n_estimators: 100
    ├─ max_depth: 6
    ├─ learning_rate: 0.1
    └─ random_state: 42
    ↓
预测结果 (0 或 1)
```

### 技术栈

| 组件 | 技术 | 版本 |
|-----|------|------|
| 后端框架 | Flask | latest |
| 机器学习 | XGBoost | latest |
| 预处理 | scikit-learn | latest |
| 数据处理 | pandas, numpy | latest |
| 模型序列化 | joblib | latest |
| 前端 | HTML5 + CSS3 + JavaScript | - |

## 特征工程

### 与训练时保持一致的转换

1. **年龄转换**
   ```python
   age_years = round(age / 365)
   ```

2. **BMI 计算**
   ```python
   bmi = weight / ((height / 100) ** 2)
   ```

3. **特征顺序**
   - age_years, gender, height, weight, bmi
   - ap_hi, ap_lo, cholesterol, gluc
   - smoke, alco, active

## 测试示例

### 示例 1: 低风险患者

```bash
curl -X POST http://localhost:5000/predict_cardio \
  -H "Content-Type: application/json" \
  -d '{
    "age": 14600,
    "gender": 1,
    "height": 165,
    "weight": 55,
    "ap_hi": 110,
    "ap_lo": 70,
    "cholesterol": 1,
    "gluc": 1,
    "smoke": 0,
    "alco": 0,
    "active": 1
  }'
```

### 示例 2: 高风险患者

```bash
curl -X POST http://localhost:5000/predict_cardio \
  -H "Content-Type: application/json" \
  -d '{
    "age": 22000,
    "gender": 2,
    "height": 172,
    "weight": 95,
    "ap_hi": 160,
    "ap_lo": 100,
    "cholesterol": 3,
    "gluc": 3,
    "smoke": 1,
    "alco": 1,
    "active": 0
  }'
```

## 常见问题

### Q1: 运行 app.py 提示"模型未加载"？
**A**: 请先运行 `train_and_save.py` 训练并保存模型。

### Q2: 端口 5000 被占用？
**A**: 修改 `app.py` 中的端口号：
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Q3: 预测结果准确吗？
**A**: 模型准确率约 73%，仅供参考，不能作为医疗诊断依据。

### Q4: 如何提高模型准确率？
**A**: 可以尝试：
- 调整 XGBoost 参数
- 增加特征工程
- 使用更多数据
- 尝试其他算法

### Q5: 可以在生产环境使用吗？
**A**: 当前是演示版本，生产环境需要：
- 使用 Gunicorn/uWSGI 部署
- 添加认证和限流
- 完善错误处理
- 添加日志监控

## 性能指标

### 模型性能

- **训练集准确率**: ~74%
- **测试集准确率**: ~73%
- **交叉验证准确率**: ~73%
- **预测速度**: < 100ms

### 系统性能

- **模型加载时间**: < 1 秒
- **单次预测时间**: < 50ms
- **并发支持**: 取决于硬件

## 注意事项

⚠️ **重要提示**:

1. 本系统仅供学习和研究使用
2. 预测结果不能作为医疗诊断依据
3. 如有健康问题，请咨询专业医生
4. 模型基于历史数据训练，可能存在偏差
5. 确保输入数据的准确性和真实性

## 后续改进

可选的功能增强：

- [ ] 增加模型可解释性（SHAP值）
- [ ] 支持批量预测
- [ ] 添加用户认证系统
- [ ] 保存预测历史记录
- [ ] 数据可视化仪表板
- [ ] 移动端适配
- [ ] 多语言支持
- [ ] Docker 容器化部署

## 联系方式

如有问题或建议，请联系开发团队。

---

**CardioAI - 心血管疾病智能辅助系统**  
Module 2: TabularFlow 风险预测模型 v1.0
