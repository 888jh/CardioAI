"""
CardioAI - 心血管疾病智能辅助系统
Module 1: 数据可视化分析仪表板

功能：
- 数据加载与缓存
- 特征工程（年龄转换、BMI计算、类别转换）
- 数据清洗（血压异常值过滤）
- 交互式可视化分析
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="CardioAI - 心血管疾病数据分析",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 数据加载函数 ====================
@st.cache_data
def load_data():
    """
    加载心血管疾病数据
    使用缓存优化性能
    """
    data_path = "D:/cursor_pro/pro1/data/心血管疾病.xlsx"
    
    try:
        if not os.path.exists(data_path):
            st.error(f"❌ 数据文件不存在: {data_path}")
            st.stop()
        
        df = pd.read_excel(data_path)
        return df
    
    except Exception as e:
        st.error(f"❌ 数据加载失败: {str(e)}")
        st.stop()

# ==================== 数据清洗与特征工程 ====================
@st.cache_data
def process_data(df):
    """
    数据清洗和特征工程
    """
    # 复制数据避免修改原始数据
    df = df.copy()
    
    # 记录原始数据量
    original_count = len(df)
    
    # 1. 特征工程：年龄转换（天 -> 年）
    df['age_years'] = round(df['age'] / 365)
    
    # 2. 特征工程：计算 BMI
    df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
    
    # 3. 特征工程：BMI 分类（中国标准）
    def categorize_bmi(bmi):
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "超重"
        else:
            return "肥胖"
    
    df['bmi_category'] = df['bmi'].apply(categorize_bmi)
    
    # 4. 特征工程：胆固醇描述性转换
    cholesterol_map = {1: "正常", 2: "高于正常", 3: "远高于正常"}
    df['cholesterol_desc'] = df['cholesterol'].map(cholesterol_map)
    
    # 5. 特征工程：血糖描述性转换
    gluc_map = {1: "正常", 2: "高于正常", 3: "远高于正常"}
    df['gluc_desc'] = df['gluc'].map(gluc_map)
    
    # 6. 数据清洗：删除血压异常值
    # 条件1: 舒张压 < 收缩压（物理规律）
    df = df[df['ap_lo'] < df['ap_hi']]
    
    # 条件2: 收缩压在合理范围 [90, 250]
    df = df[(df['ap_hi'] >= 90) & (df['ap_hi'] <= 250)]
    
    # 条件3: 舒张压在合理范围 [60, 150]
    df = df[(df['ap_lo'] >= 60) & (df['ap_lo'] <= 150)]
    
    # 记录清洗后数据量
    cleaned_count = len(df)
    removed_count = original_count - cleaned_count
    
    return df, original_count, removed_count

# ==================== 主应用程序 ====================
def main():
    # 页面标题
    st.title("❤️ CardioAI - 心血管疾病智能辅助系统")
    st.markdown("### 📊 数据可视化分析仪表板")
    st.info("💡 本系统基于 70,000 条心血管疾病数据，提供交互式数据探索和可视化分析")
    
    # 加载数据（显示加载动画）
    with st.spinner("⏳ 正在加载数据..."):
        raw_df = load_data()
        df, original_count, removed_count = process_data(raw_df)
    
    # ==================== 侧边栏筛选器 ====================
    st.sidebar.header("🔍 数据筛选")
    st.sidebar.markdown("---")
    
    # 年龄范围滑块
    age_min = int(df['age_years'].min())
    age_max = int(df['age_years'].max())
    age_range = st.sidebar.slider(
        "年龄范围（岁）",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
        help="拖动滑块选择年龄范围"
    )
    
    # 性别多选框
    gender_options = st.sidebar.multiselect(
        "性别",
        options=[1, 2],
        default=[1, 2],
        format_func=lambda x: "👩 女性" if x == 1 else "👨 男性",
        help="选择要分析的性别"
    )
    
    # 心血管疾病状态多选框
    cardio_options = st.sidebar.multiselect(
        "心血管疾病状态",
        options=[0, 1],
        default=[0, 1],
        format_func=lambda x: "✅ 无疾病" if x == 0 else "⚠️ 有疾病",
        help="选择要分析的疾病状态"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 提示：调整筛选条件后，所有图表会自动更新")
    
    # ==================== 数据筛选 ====================
    # 检查筛选条件是否为空
    if not gender_options or not cardio_options:
        st.warning("⚠️ 请至少选择一个性别和一个疾病状态")
        st.stop()
    
    # 应用筛选条件
    filtered_df = df[
        (df['age_years'] >= age_range[0]) &
        (df['age_years'] <= age_range[1]) &
        (df['gender'].isin(gender_options)) &
        (df['cardio'].isin(cardio_options))
    ]
    
    # 检查筛选后是否有数据
    if len(filtered_df) == 0:
        st.warning("⚠️ 当前筛选条件下没有数据，请调整筛选条件")
        st.stop()
    
    # ==================== 关键指标展示 ====================
    st.markdown("### 📈 关键指标")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="筛选后记录数",
            value=f"{len(filtered_df):,}",
            delta=f"占总数 {len(filtered_df)/len(df)*100:.1f}%"
        )
    
    with col2:
        risk_rate = (filtered_df['cardio'].sum() / len(filtered_df)) * 100
        st.metric(
            label="心血管疾病风险率",
            value=f"{risk_rate:.1f}%",
            delta=None
        )
    
    with col3:
        st.metric(
            label="数据清洗统计",
            value=f"{removed_count:,} 条",
            delta=f"清洗率 {removed_count/original_count*100:.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        avg_age = filtered_df['age_years'].mean()
        st.metric(
            label="平均年龄",
            value=f"{avg_age:.1f} 岁"
        )
    
    with col5:
        avg_bmi = filtered_df['bmi'].mean()
        st.metric(
            label="平均 BMI",
            value=f"{avg_bmi:.2f}"
        )
    
    st.markdown("---")
    
    # ==================== 可视化图表 ====================
    st.markdown("### 📊 数据可视化分析")
    
    # 创建两列布局
    chart_col1, chart_col2 = st.columns(2)
    
    # 图表1: 年龄分布直方图
    with chart_col1:
        st.markdown("#### 1️⃣ 年龄分布与疾病关系")
        
        # 创建疾病状态的友好标签
        filtered_df_plot = filtered_df.copy()
        filtered_df_plot['疾病状态'] = filtered_df_plot['cardio'].map({
            0: "无疾病", 
            1: "有疾病"
        })
        
        fig1 = px.histogram(
            filtered_df_plot,
            x='age_years',
            color='疾病状态',
            barmode='overlay',
            nbins=30,
            opacity=0.7,
            title="年龄分布直方图（按疾病状态分组）",
            labels={'age_years': '年龄（岁）', 'count': '人数'},
            color_discrete_map={'无疾病': '#2ecc71', '有疾病': '#e74c3c'}
        )
        
        fig1.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("💡 观察不同年龄段的疾病分布情况，红色表示患病，绿色表示健康")
    
    # 图表2: BMI分类与心血管疾病关系
    with chart_col2:
        st.markdown("#### 2️⃣ BMI 分类与疾病关系")
        
        # 按 BMI 分类和疾病状态分组统计
        bmi_cardio_counts = filtered_df.groupby(['bmi_category', 'cardio']).size().reset_index(name='count')
        bmi_cardio_counts['疾病状态'] = bmi_cardio_counts['cardio'].map({
            0: "无疾病",
            1: "有疾病"
        })
        
        # 设置 BMI 分类的顺序
        bmi_order = ['偏瘦', '正常', '超重', '肥胖']
        bmi_cardio_counts['bmi_category'] = pd.Categorical(
            bmi_cardio_counts['bmi_category'],
            categories=bmi_order,
            ordered=True
        )
        bmi_cardio_counts = bmi_cardio_counts.sort_values('bmi_category')
        
        fig2 = px.bar(
            bmi_cardio_counts,
            x='bmi_category',
            y='count',
            color='疾病状态',
            barmode='stack',
            title="BMI 分类堆叠柱状图",
            labels={'bmi_category': 'BMI 分类', 'count': '人数'},
            color_discrete_map={'无疾病': '#2ecc71', '有疾病': '#e74c3c'}
        )
        
        fig2.update_layout(
            height=400,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("💡 观察不同 BMI 分类下的疾病分布，堆叠显示患病和健康人数")
    
    st.markdown("---")
    
    # ==================== 数据概览表格 ====================
    st.markdown("### 📋 数据概览")
    
    # 选择要显示的列
    display_columns = [
        'id', 'age_years', 'gender', 'height', 'weight', 'bmi', 'bmi_category',
        'ap_hi', 'ap_lo', 'cholesterol_desc', 'gluc_desc', 'cardio'
    ]
    
    # 创建友好的列名映射
    column_names = {
        'id': 'ID',
        'age_years': '年龄（岁）',
        'gender': '性别',
        'height': '身高（cm）',
        'weight': '体重（kg）',
        'bmi': 'BMI',
        'bmi_category': 'BMI分类',
        'ap_hi': '收缩压',
        'ap_lo': '舒张压',
        'cholesterol_desc': '胆固醇',
        'gluc_desc': '血糖',
        'cardio': '心血管疾病'
    }
    
    display_df = filtered_df[display_columns].copy()
    display_df['gender'] = display_df['gender'].map({1: '女性', 2: '男性'})
    display_df['cardio'] = display_df['cardio'].map({0: '无', 1: '有'})
    display_df = display_df.rename(columns=column_names)
    
    # 显示前100行数据
    st.dataframe(
        display_df.head(100),
        use_container_width=True,
        height=400
    )
    
    st.caption(f"📊 显示前 100 条记录，共 {len(filtered_df):,} 条数据")
    
    # ==================== 页脚信息 ====================
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #7f8c8d;'>
            <p>💻 CardioAI - 心血管疾病智能辅助系统 | Module 1: 数据可视化仪表板</p>
            <p>🔬 基于 70,000 条真实心血管疾病数据 | 采用 Streamlit + Plotly 技术栈</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==================== 运行应用 ====================
if __name__ == "__main__":
    main()
