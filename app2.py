import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid', font='WenQuanYi Zen Hei', rc={'axes.unicode_minus': False})

# 页面配置
st.set_page_config(
    page_title="企业数字化转型数据查询分析系统",
    page_icon="[表情]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8F9FA;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .metric-label {
        font-size: 1rem;
        color: #6C757D;
    }
    .chart-container {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-title {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .data-table {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .footer {
        text-align: center;
        margin-top: 2rem;
        color: #6C757D;
        font-size: 0.9rem;
    }
    .company-info-card {
        background-color: #F8F9FA;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .company-info-title {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
        border-bottom: 1px solid #e9ecef;
        padding-bottom: 0.5rem;
    }
    .info-item {
        display: flex;
        margin-bottom: 0.8rem;
    }
    .info-label {
        font-weight: bold;
        width: 120px;
        color: #495057;
    }
    .info-value {
        flex: 1;
    }
    .tech-card {
        background-color: #FFFFFF;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        height: 100%;
    }
    .tech-title {
        font-size: 1.2rem;
        color: #1E88E5;
        margin-bottom: 0.8rem;
    }
    .tech-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .tech-label {
        font-size: 0.9rem;
        color: #6C757D;
    }
    .welcome-container {
        background-color: #F8F9FA;
        border-radius: 0.5rem;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .welcome-title {
        font-size: 2rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .welcome-text {
        font-size: 1.1rem;
        color: #495057;
        line-height: 1.6;
    }
    .sidebar-stats {
        background-color: #F8F9FA;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-stat-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    }
    .sidebar-stat-label {
        color: #495057;
    }
    .sidebar-stat-value {
        font-weight: bold;
        color: #1E88E5;
    }
</style>
""", unsafe_allow_html=True)

# 标题和描述
st.markdown('<h1 class="main-header">企业数字化转型数据查询分析系统</h1>', unsafe_allow_html=True)
st.markdown("本系统提供企业数字化技术应用数据查询与分析功能，支持多维度数据展示和可视化分析。")

# 加载数据
@st.cache_data
def load_data():
    try:
        # 使用相对路径读取Excel文件
        file_path = "1999-2023.xlsx"
        df = pd.read_excel(file_path)
        
        # 数据清洗
        # 过滤掉企业名称为"0"、空值、NaN的无效记录
        df = df[~df['企业名称'].isin(['0', '', np.nan, 'nan'])]
        
        # 确保年份是整数类型
        df['年份'] = pd.to_numeric(df['年份'], errors='coerce').fillna(0).astype(int)
        
        # 确保数值列是数值类型
        numeric_cols = ['总词频', '人工智能', '区块链', '大数据', '云计算', '物联网', '5G通信', 
                        '数字平台', '数字安全', '智慧行业应用', '企业数字化', '数字运营', 
                        '数字人才', '技术多样性', '技术种类数', '数字化程度', '上年总词频', 
                        '年度增长率', '行业公司数']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 处理缺失值
        df = df.fillna(0)
        
        # 确保字符串列是字符串类型
        string_cols = ['股票代码', '企业名称', '行业代码', '行业名称']
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        return df
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return None

# 侧边栏
st.sidebar.markdown('<h2 class="sidebar-title">查询条件</h2>', unsafe_allow_html=True)

# 加载数据
df = load_data()

if df is not None:
    # 获取所有不重复的企业名称并排序
    companies = sorted(df['企业名称'].unique())
    
    # 企业选择下拉框
    st.sidebar.subheader("企业查询")
    selected_company = st.sidebar.selectbox(
        "选择企业",
        options=[""] + companies,
        index=0
    )
    
    # 获取年份范围
    min_year = int(df['年份'].min())
    max_year = int(df['年份'].max())
    
    # 侧边栏筛选条件
    st.sidebar.subheader("年份范围")
    year_range = st.sidebar.slider(
        "选择年份范围",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    # 行业多选
    st.sidebar.subheader("行业选择")
    industries = sorted(df['行业名称'].unique())
    selected_industries = st.sidebar.multiselect(
        "选择行业（可多选）",
        options=industries,
        default=industries[:5]  # 默认选择前5个行业
    )
    
    # 侧边栏数据概览
    st.sidebar.markdown('<div class="sidebar-stats">', unsafe_allow_html=True)
    st.sidebar.markdown('<h3 class="sidebar-title">数据概览</h3>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="sidebar-stat-item">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-stat-label">企业总数:</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="sidebar-stat-value">{df["企业名称"].nunique()}</div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="sidebar-stat-item">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-stat-label">行业总数:</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="sidebar-stat-value">{df["行业名称"].nunique()}</div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('<div class="sidebar-stat-item">', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="sidebar-stat-label">年份范围:</div>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="sidebar-stat-value">{min_year} - {max_year}</div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # 数据筛选
    filtered_df = df[
        (df['年份'] >= year_range[0]) & 
        (df['年份'] <= year_range[1])
    ]
    
    if selected_industries:
        filtered_df = filtered_df[filtered_df['行业名称'].isin(selected_industries)]
    
    # 如果选择了特定企业，则展示该企业的详细信息
    if selected_company:
        # 获取该企业的所有数据
        company_data = df[df['企业名称'] == selected_company]
        
        # 获取企业基本信息
        company_info = company_data.iloc[0]
        
        # 企业基础信息卡片
        st.markdown('<div class="company-info-card">', unsafe_allow_html=True)
        st.markdown(f'<h2 class="company-info-title">{selected_company} 企业详情</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">股票代码:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{company_info["股票代码"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">所属行业:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{company_info["行业名称"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">行业代码:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{company_info["行业代码"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">数据年份范围:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{company_data["年份"].min()} - {company_data["年份"].max()}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">记录数:</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{len(company_data)}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="info-item">', unsafe_allow_html=True)
            st.markdown('<div class="info-label">最新数字化程度:</div>', unsafe_allow_html=True)
            latest_year = company_data["年份"].max()
            latest_data = company_data[company_data["年份"] == latest_year].iloc[0]
            st.markdown(f'<div class="info-value">{latest_data["数字化程度"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 企业数字化指标概览
        st.header("企业数字化指标概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.markdown('<div class="tech-title">总词频</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tech-value">{company_data["总词频"].sum():.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="tech-label">累计总词频</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.markdown('<div class="tech-title">技术种类数</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tech-value">{latest_data["技术种类数"]:.0f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="tech-label">最新年份数据</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.markdown('<div class="tech-title">数字化程度</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tech-value">{latest_data["数字化程度"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="tech-label">最新年份数据</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="tech-card">', unsafe_allow_html=True)
            st.markdown('<div class="tech-title">技术多样性</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="tech-value">{latest_data["技术多样性"]:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="tech-label">最新年份数据</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 技术应用趋势图表
        st.header("技术应用趋势")
        
        # 选择要展示的技术指标
        tech_metrics = ['人工智能', '区块链', '大数据', '云计算', '物联网', '5G通信', 
                        '数字平台', '数字安全', '智慧行业应用']
        
        # 创建多子图
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=tech_metrics,
            vertical_spacing=0.08,
            horizontal_spacing=0.08
        )
        
        # 添加每个技术的趋势线
        for i, tech in enumerate(tech_metrics):
            row = i // 3 + 1
            col = i % 3 + 1
            
            fig.add_trace(
                go.Scatter(
                    x=company_data['年份'],
                    y=company_data[tech],
                    mode='lines+markers',
                    name=tech,
                    line=dict(width=2),
                    marker=dict(size=6)
                ),
                row=row, col=col
            )
        
        # 更新布局
        fig.update_layout(
            height=800,
            title_text=f"{selected_company} 技术应用趋势",
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 年度增长率图表
        st.header("年度增长率分析")
        
        # 创建增长率图表
        growth_fig = px.bar(
            company_data,
            x='年份',
            y='年度增长率',
            title=f"{selected_company} 年度增长率",
            labels={'年度增长率': '增长率 (%)', '年份': '年份'},
            color='年度增长率',
            color_continuous_scale='RdYlGn'
        )
        
        # 添加零线
        growth_fig.add_hline(y=0, line_dash="dash", line_color="red")
        
        growth_fig.update_layout(
            xaxis_title="年份",
            yaxis_title="增长率 (%)"
        )
        
        st.plotly_chart(growth_fig, use_container_width=True)
        
        # 行业对比分析
        st.header("行业对比分析")
        
        # 获取同行业其他企业
        industry = company_info['行业名称']
        industry_companies = df[df['行业名称'] == industry]
        
        # 计算行业平均数字化程度
        industry_avg = industry_companies.groupby('年份')['数字化程度'].mean().reset_index()
        industry_avg.columns = ['年份', '行业平均']
        
        # 获取该企业的数字化程度
        company_digital = company_data[['年份', '数字化程度']]
        company_digital.columns = ['年份', '企业数字化程度']
        
        # 合并数据
        comparison_df = pd.merge(industry_avg, company_digital, on='年份', how='inner')
        
        # 创建对比图表
        comparison_fig = go.Figure()
        
        # 添加行业平均线
        comparison_fig.add_trace(go.Scatter(
            x=comparison_df['年份'],
            y=comparison_df['行业平均'],
            mode='lines+markers',
            name='行业平均',
            line=dict(color='blue', width=2),
            marker=dict(size=8)
        ))
        
        # 添加企业线
        comparison_fig.add_trace(go.Scatter(
            x=comparison_df['年份'],
            y=comparison_df['企业数字化程度'],
            mode='lines+markers',
            name=selected_company,
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))
        
        # 更新布局
        comparison_fig.update_layout(
            title=f"{selected_company} 与 {industry} 行业数字化程度对比",
            xaxis_title="年份",
            yaxis_title="数字化程度",
            legend_title="数据来源"
        )
        
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        # 企业详细数据表格
        st.header("企业详细数据")
        st.dataframe(
            company_data.sort_values('年份', ascending=False),
            use_container_width=True,
            height=400
        )
        
    else:
        # 未选择企业时，显示数据概览和说明
        st.markdown('<div class="welcome-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="welcome-title">欢迎使用企业数字化转型数据查询分析系统</h2>', unsafe_allow_html=True)
        st.markdown('<p class="welcome-text">请在左侧侧边栏选择企业，查看企业详细信息和分析报告。</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 数据概览仪表盘
        st.header("数据概览仪表盘")
        
        # 创建指标卡片
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{len(df)}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">记录总数</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df["企业名称"].nunique()}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">企业数量</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{df["行业名称"].nunique()}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">行业数量</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_digital = df["数字化程度"].mean()
            st.markdown(f'<div class="metric-value">{avg_digital:.2f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">平均数字化程度</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 数据表格展示
        st.header("数据详情")
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        
        # 使用Streamlit的数据表格功能
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=400
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 多维度可视化图表
        st.header("多维度可视化分析")
        
        # 创建选项卡
        tab1, tab2, tab3, tab4 = st.tabs(["总词频趋势", "技术应用对比", "行业数字化分布", "企业数字化排名"])
        
        with tab1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("总词频年度趋势")
            
            # 按年份分组计算总词频平均值
            trend_data = filtered_df.groupby('年份')['总词频'].mean().reset_index()
            
            # 创建折线图
            fig = px.line(
                trend_data, 
                x='年份', 
                y='总词频',
                title='总词频年度趋势',
                labels={'总词频': '平均总词频', '年份': '年份'},
                markers=True
            )
            
            # 添加趋势线
            fig.update_layout(
                hovermode='x unified',
                xaxis_title="年份",
                yaxis_title="平均总词频"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("各项技术应用对比")
            
            # 选择要对比的技术指标
            tech_metrics = ['人工智能', '区块链', '大数据', '云计算', '物联网', '5G通信', 
                            '数字平台', '数字安全', '智慧行业应用']
            
            # 计算各技术指标的平均值
            tech_data = filtered_df[tech_metrics].mean().reset_index()
            tech_data.columns = ['技术', '平均值']
            
            # 创建柱状图
            fig = px.bar(
                tech_data,
                x='技术',
                y='平均值',
                title='各项技术应用平均值对比',
                labels={'平均值': '平均词频', '技术': '技术类型'},
                color='技术'
            )
            
            fig.update_layout(
                xaxis_title="技术类型",
                yaxis_title="平均词频",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab3:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("行业数字化程度分布")
            
            # 按行业分组计算数字化程度
            industry_data = filtered_df.groupby('行业名称')['数字化程度'].mean().reset_index()
            industry_data = industry_data.sort_values('数字化程度', ascending=False)
            
            # 创建水平柱状图
            fig = px.bar(
                industry_data,
                x='数字化程度',
                y='行业名称',
                title='行业数字化程度分布',
                labels={'数字化程度': '平均数字化程度', '行业名称': '行业名称'},
                orientation='h',
                color='数字化程度',
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                xaxis_title="平均数字化程度",
                yaxis_title="行业名称",
                height=max(400, len(industry_data) * 20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with tab4:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("企业数字化水平排名")
            
            # 按企业分组计算数字化程度
            company_data = filtered_df.groupby('企业名称')['数字化程度'].mean().reset_index()
            company_data = company_data.sort_values('数字化程度', ascending=False).head(20)
            
            # 创建柱状图
            fig = px.bar(
                company_data,
                x='企业名称',
                y='数字化程度',
                title='企业数字化水平TOP20',
                labels={'数字化程度': '平均数字化程度', '企业名称': '企业名称'},
                color='数字化程度',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                xaxis_title="企业名称",
                yaxis_title="平均数字化程度",
                xaxis={'categoryorder': 'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 相关性分析
        st.header("指标相关性分析")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        
        # 选择要分析相关性的指标
        correlation_metrics = st.multiselect(
            "选择要分析相关性的指标",
            options=tech_metrics + ['总词频', '数字化程度', '技术多样性'],
            default=['人工智能', '大数据', '云计算', '数字化程度']
        )
        
        if correlation_metrics:
            # 计算相关性矩阵
            correlation_df = filtered_df[correlation_metrics].corr()
            
            # 创建热力图
            fig = px.imshow(
                correlation_df,
                text_auto=True,
                aspect="auto",
                color_continuous_scale='RdBu_r',
                title="指标相关性热力图"
            )
            
            fig.update_layout(
                width=800,
                height=600
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("请至少选择一个指标进行相关性分析")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # PDF导出功能
    st.header("导出功能")
    
    def generate_pdf(df, selected_company, year_range, selected_industries):
        """生成PDF报告"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch, cm
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # 创建PDF缓冲区
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            
            # 注册中文字体
            try:
                # 尝试注册SimHei字体
                pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
                chinese_font = 'SimHei'
            except:
                try:
                    # 尝试注册微软雅黑字体
                    pdfmetrics.registerFont(TTFont('MicrosoftYaHei', 'MicrosoftYaHei.ttf'))
                    chinese_font = 'MicrosoftYaHei'
                except:
                    # 如果都找不到，使用默认字体
                    chinese_font = 'Helvetica'
            
            # 创建中文字体样式
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1,  # 居中
                fontName=chinese_font
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12,
                fontName=chinese_font
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                fontName=chinese_font
            )
            
            # 添加标题
            elements.append(Paragraph("企业数字化转型数据分析报告", title_style))
            elements.append(Spacer(1, 12))
            
            # 添加查询条件
            elements.append(Paragraph("查询条件:", heading_style))
            elements.append(Paragraph(f"年份范围: {year_range[0]}年 - {year_range[1]}年", normal_style))
            elements.append(Paragraph(f"选择行业: {', '.join(selected_industries) if selected_industries else '全部行业'}", normal_style))
            if selected_company:
                elements.append(Paragraph(f"选择企业: {selected_company}", normal_style))
            elements.append(Spacer(1, 12))
            
            # 如果选择了特定企业，添加企业详情
            if selected_company:
                # 获取该企业的所有数据
                company_data = df[df['企业名称'] == selected_company]
                
                # 获取企业基本信息
                company_info = company_data.iloc[0]
                
                # 添加企业基本信息
                elements.append(Paragraph("企业基本信息:", heading_style))
                company_info_data = [
                    ['项目', '值'],
                    ['企业名称', str(company_info['企业名称'])],
                    ['股票代码', str(company_info['股票代码'])],
                    ['所属行业', str(company_info['行业名称'])],
                    ['行业代码', str(company_info['行业代码'])],
                    ['数据年份范围', f"{company_data['年份'].min()} - {company_data['年份'].max()}"],
                    ['记录数', str(len(company_data))],
                    ['最新数字化程度', f"{company_data[company_data['年份'] == company_data['年份'].max()]['数字化程度'].iloc[0]:.2f}"]
                ]
                company_info_table = Table(company_info_data, colWidths=[3*cm, 8*cm])
                company_info_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(company_info_table)
                elements.append(Spacer(1, 12))
                
                # 添加企业数字化指标
                elements.append(Paragraph("企业数字化指标:", heading_style))
                latest_year = company_data['年份'].max()
                latest_data = company_data[company_data['年份'] == latest_year].iloc[0]
                
                metrics_data = [
                    ['指标', '值'],
                    ['总词频', f"{company_data['总词频'].sum():.0f}"],
                    ['技术种类数', f"{latest_data['技术种类数']:.0f}"],
                    ['数字化程度', f"{latest_data['数字化程度']:.2f}"],
                    ['技术多样性', f"{latest_data['技术多样性']:.2f}"]
                ]
                metrics_table = Table(metrics_data, colWidths=[3*cm, 5*cm])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(metrics_table)
                elements.append(Spacer(1, 12))
                
                # 添加企业详细数据
                elements.append(Paragraph("企业详细数据:", heading_style))
                # 只取前20条记录
                company_table_data = [company_data.columns.tolist()] + company_data.sort_values('年份', ascending=False).head(20).values.tolist()
                # 确保所有数据都转换为字符串
                company_table_data = [[str(cell) for cell in row] for row in company_table_data]
                company_table = Table(company_table_data)
                company_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(company_table)
                elements.append(Spacer(1, 12))
            else:
                # 添加数据概览
                elements.append(Paragraph("数据概览:", heading_style))
                overview_data = [
                    ['指标', '值'],
                    ['记录总数', str(len(df))],
                    ['企业数量', str(df["企业名称"].nunique())],
                    ['行业数量', str(df["行业名称"].nunique())],
                    ['平均数字化程度', f"{df['数字化程度'].mean():.2f}"]
                ]
                overview_table = Table(overview_data, colWidths=[3*cm, 5*cm])
                overview_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(overview_table)
                elements.append(Spacer(1, 12))
                
                # 添加数据表格
                elements.append(Paragraph("数据详情:", heading_style))
                # 只取前20条记录
                table_data = [df.columns.tolist()] + df.head(20).values.tolist()
                # 确保所有数据都转换为字符串
                table_data = [[str(cell) for cell in row] for row in table_data]
                data_table = Table(table_data)
                data_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), chinese_font),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), chinese_font),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(data_table)
                elements.append(Spacer(1, 12))
            
            # 添加分析结论
            elements.append(Paragraph("分析结论:", heading_style))
            
            # 计算一些关键指标
            if selected_company:
                # 企业特定分析
                industry = company_info['行业名称']
                industry_companies = df[df['行业名称'] == industry]
                industry_avg = industry_companies['数字化程度'].mean()
                company_avg = company_data['数字化程度'].mean()
                
                # 找出企业应用最多的技术
                tech_metrics = ['人工智能', '区块链', '大数据', '云计算', '物联网', '5G通信', 
                                '数字平台', '数字安全', '智慧行业应用']
                top_tech = company_data[tech_metrics].sum().idxmax()
                
                conclusions = [
                    f"1. {selected_company}的数字化程度为{company_avg:.2f}，{industry}行业平均数字化程度为{industry_avg:.2f}。",
                    f"2. {selected_company}应用最广泛的技术是{top_tech}。",
                    f"3. {selected_company}的数据年份范围为{company_data['年份'].min()} - {company_data['年份'].max()}，共{len(company_data)}条记录。",
                    f"4. {selected_company}的最新数字化程度为{latest_data['数字化程度']:.2f}。"
                ]
            else:
                # 整体数据分析
                top_industry = df.groupby('行业名称')['数字化程度'].mean().idxmax()
                top_company = df.groupby('企业名称')['数字化程度'].mean().idxmax()
                tech_metrics = ['人工智能', '区块链', '大数据', '云计算', '物联网', '5G通信', 
                                '数字平台', '数字安全', '智慧行业应用']
                top_tech = df[tech_metrics].mean().idxmax()
                
                conclusions = [
                    f"1. 在所选时间段内，数字化程度最高的行业是{top_industry}。",
                    f"2. 数字化水平最高的企业是{top_company}。",
                    f"3. 应用最广泛的技术是{top_tech}。",
                    f"4. 企业平均数字化程度为{df['数字化程度'].mean():.2f}。"
                ]
            
            for conclusion in conclusions:
                elements.append(Paragraph(conclusion, normal_style))
            
            elements.append(Spacer(1, 12))
            
            # 添加生成时间
            elements.append(Paragraph(f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            
            # 构建PDF
            doc.build(elements)
            
            # 获取PDF数据
            pdf_data = buffer.getvalue()
            buffer.close()
            
            return pdf_data
            
        except Exception as e:
            st.error(f"PDF生成失败: {e}")
            return None
    
    # 生成PDF文件名
    if selected_company:
        filename = f"{selected_company}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    else:
        filename = f"企业数字化转型数据_{year_range[0]}-{year_range[1]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    
    # 生成PDF数据
    pdf_data = generate_pdf(filtered_df, selected_company, year_range, selected_industries)
    
    # 显示下载按钮
    if pdf_data:
        st.download_button(
            label="[表情] 下载PDF分析报告",
            data=pdf_data,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True
        )
    else:
        st.warning("PDF生成失败，请稍后重试。")
    
    # 页脚
    st.markdown('<div class="footer">© 2023 企业数字化转型数据查询分析系统 | 数据更新时间: 2023-12-10</div>', unsafe_allow_html=True)
else:
    st.error("无法加载数据，请检查文件路径或文件格式是否正确。")
