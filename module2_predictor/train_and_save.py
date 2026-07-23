"""
CardioAI - 心血管疾病智能辅助系统
Module 2: 模型训练脚本

功能：
- 加载和清洗数据
- 特征工程
- 构建 Pipeline（预处理 + XGBoost）
- 训练模型并保存

执行方式：
    D:\software\anaconda3\envs\cardioenv\python.exe train_and_save.py
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, train_test_split
from xgboost import XGBClassifier
import joblib
import os
from datetime import datetime

def main():
    print("=" * 60)
    print("CardioAI - 心血管疾病预测模型训练")
    print("=" * 60)
    
    # ==================== 1. 数据加载 ====================
    print("\n[1/6] 加载数据...")
    data_path = "D:/cursor_pro/pro1/data/心血管疾病.xlsx"
    
    if not os.path.exists(data_path):
        print(f"错误：数据文件不存在 - {data_path}")
        return
    
    df = pd.read_excel(data_path)
    print(f"  [OK] 成功加载 {len(df):,} 条原始数据")
    print(f"  [OK] 数据维度: {df.shape}")
    
    # ==================== 2. 特征工程 ====================
    print("\n[2/6] 特征工程...")
    
    # 年龄转换（天 -> 年）
    df['age_years'] = round(df['age'] / 365)
    print(f"  [OK] 年龄转换完成 (天数 -> 年龄)")
    
    # 计算 BMI
    df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
    print(f"  [OK] BMI 计算完成")
    
    # ==================== 3. 数据清洗 ====================
    print("\n[3/6] 数据清洗...")
    original_count = len(df)
    
    # 删除血压异常值
    df = df[df['ap_lo'] < df['ap_hi']]  # 舒张压 < 收缩压
    df = df[(df['ap_hi'] >= 90) & (df['ap_hi'] <= 250)]  # 收缩压范围
    df = df[(df['ap_lo'] >= 60) & (df['ap_lo'] <= 150)]  # 舒张压范围
    
    cleaned_count = len(df)
    removed_count = original_count - cleaned_count
    print(f"  [OK] 清洗完成")
    print(f"    - 保留数据: {cleaned_count:,} 条")
    print(f"    - 删除数据: {removed_count:,} 条 ({removed_count/original_count*100:.2f}%)")
    
    # ==================== 4. 特征选择 ====================
    print("\n[4/6] 特征选择...")
    
    # 删除不需要的列
    df = df.drop(['id', 'age'], axis=1)
    print(f"  [OK] 删除 id 和原始 age 列")
    
    # 分离特征和目标
    X = df.drop('cardio', axis=1)
    y = df['cardio']
    
    print(f"  [OK] 特征数量: {X.shape[1]}")
    print(f"  [OK] 特征列表: {list(X.columns)}")
    print(f"  [OK] 目标分布: 无病={sum(y==0):,} ({sum(y==0)/len(y)*100:.1f}%), "
          f"有病={sum(y==1):,} ({sum(y==1)/len(y)*100:.1f}%)")
    
    # ==================== 5. 构建 Pipeline ====================
    print("\n[5/6] 构建 Pipeline...")
    
    # 定义特征类型
    continuous_features = ['age_years', 'height', 'weight', 'bmi', 'ap_hi', 'ap_lo']
    categorical_features = ['gender', 'cholesterol', 'gluc', 'smoke', 'alco', 'active']
    
    print(f"  [OK] 连续特征 ({len(continuous_features)}): {continuous_features}")
    print(f"  [OK] 分类特征 ({len(categorical_features)}): {categorical_features}")
    
    # 创建预处理器
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), continuous_features),
            ('cat', OneHotEncoder(drop='first', sparse_output=False), categorical_features)
        ],
        verbose_feature_names_out=False
    )
    
    # 创建完整 Pipeline
    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric='logloss',
            verbosity=1
        ))
    ])
    
    print(f"  [OK] Pipeline 构建完成")
    print(f"    - 预处理: StandardScaler + OneHotEncoder")
    print(f"    - 分类器: XGBClassifier")
    
    # ==================== 6. 训练模型 ====================
    print("\n[6/6] 训练模型...")
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  [OK] 数据划分: 训练集 {len(X_train):,} 条, 测试集 {len(X_test):,} 条")
    
    # 训练模型
    print(f"  [训练中] 请稍候...")
    start_time = datetime.now()
    pipeline.fit(X_train, y_train)
    train_time = (datetime.now() - start_time).total_seconds()
    print(f"  [OK] 训练完成 (耗时 {train_time:.2f} 秒)")
    
    # 评估模型
    print(f"\n  [模型评估]")
    
    # 训练集准确率
    train_score = pipeline.score(X_train, y_train)
    print(f"    - 训练集准确率: {train_score:.4f} ({train_score*100:.2f}%)")
    
    # 测试集准确率
    test_score = pipeline.score(X_test, y_test)
    print(f"    - 测试集准确率: {test_score:.4f} ({test_score*100:.2f}%)")
    
    # 5折交叉验证
    print(f"  [验证中] 5折交叉验证...")
    cv_scores = cross_val_score(pipeline, X, y, cv=5, scoring='accuracy', n_jobs=-1)
    print(f"    - 交叉验证准确率: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    print(f"    - 各折准确率: {[f'{s:.4f}' for s in cv_scores]}")
    
    # ==================== 7. 保存模型 ====================
    print("\n[7/7] 保存模型...")
    
    model_path = 'cardio_predictor_model.pkl'
    joblib.dump(pipeline, model_path)
    
    # 获取文件大小
    file_size = os.path.getsize(model_path) / (1024 * 1024)  # MB
    print(f"  [OK] 模型已保存到: {model_path}")
    print(f"  [OK] 文件大小: {file_size:.2f} MB")
    
    # ==================== 8. 完成 ====================
    print("\n" + "=" * 60)
    print("[完成] 模型训练完成！")
    print("=" * 60)
    print(f"\n[模型信息]")
    print(f"  - 训练样本数: {len(X_train):,}")
    print(f"  - 测试样本数: {len(X_test):,}")
    print(f"  - 特征数量: {X.shape[1]}")
    print(f"  - 测试准确率: {test_score:.4f}")
    print(f"  - 交叉验证准确率: {cv_scores.mean():.4f}")
    print(f"  - 模型文件: {model_path}")
    
    print(f"\n[下一步]")
    print(f"  运行 Flask 应用:")
    print(f"  D:\\software\\anaconda3\\envs\\cardioenv\\python.exe app.py")
    print()

if __name__ == "__main__":
    main()
