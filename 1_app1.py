import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile
import requests
import urllib.parse
import re
from pathlib import Path

# 忽略特定警告
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set(style='whitegrid', font='WenQuanYi Zen Hei', rc={'axes.unicode_minus': False})

# 页面配置
st.set_page_config(
    page_title="企业数字化转型数据查询系统",
    page_icon="[表情]",
    layout="wide",
    initial_sidebar_state="collapsed"  # 折叠侧边栏
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
    .sub-header {
        font-size: 1.2rem;
        color: #5E35B1;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stDataFrame {
        width: 100%;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .chart-container {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .filter-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    .company-detail-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .company-detail-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
        padding-bottom: 10px;
    }
    .company-detail-section {
        margin-bottom: 20px;
    }
    .company-detail-section-title {
        font-size: 1.2rem;
        color: #5E35B1;
        margin-bottom: 10px;
    }
    .company-detail-metric {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .company-detail-metric-label {
        font-weight: bold;
    }
    .company-detail-metric-value {
        color: #1E88E5;
    }
    .trend-chart-container {
        height: 400px;
        margin-bottom: 30px;
    }
    .tech-distribution-container {
        height: 400px;
        margin-bottom: 30px;
    }
    .industry-comparison-container {
        height: 400px;
        margin-bottom: 30px;
    }
    .data-table-container {
        margin-top: 20px;
    }
    .pdf-export-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .pdf-export-header {
        font-size: 1.5rem;
        color: #1E88E5;
        margin-bottom: 15px;
    }
    .pdf-export-section {
        margin-bottom: 20px;
    }
    .pdf-export-section-title {
        font-size: 1.2rem;
        color: #5E35B1;
        margin-bottom: 10px;
    }
    .error-message {
        padding: 15px;
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        margin-bottom: 20px;
    }
    .success-message {
        padding: 15px;
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        margin-bottom: 20px;
    }
    .info-message {
        padding: 15px;
        background-color: #e3f2fd;
        border-left: 5px solid #2196f3;
        margin-bottom: 20px;
    }
    .file-upload-container {
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }
    /* 隐藏侧边栏 */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    /* 调整主内容区域 */
    .block-container {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    /* 隐藏Streamlit的默认警告 */
    .stAlert > div {
        white-space: normal !important;
    }
</style>
""", unsafe_allow_html=True)

# 尝试从多个可能的路径加载数据文件
def find_data_file():
    # 可能的文件路径列表
    possible_paths = [
        # 当前工作目录
        "中国上市企业数字化转型指数（2007-2020）(1).xlsx",
        "./中国上市企业数字化转型指数（2007-2020）(1).xlsx",
        # 上传文件目录
        "uploaded_files/中国上市企业数字化转型指数（2007-2020）(1).xlsx",
        "./uploaded_files/中国上市企业数字化转型指数（2007-2020）(1).xlsx",
        # 原始路径
        "/home/wuying/autoglm/session_bfe1b1cb-7f09-412f-a26b-135d8a706a41/中国上市企业数字化转型指数（2007-2020）(1).xlsx",
        # 网络URL
        "https://autoglm-agent.aminer.cn/auto_fly/e5580288-9835-47be-9cfc-deac46159f7a/中国上市企业数字化转型指数（2007-2020）(1).xlsx"
    ]
    
    # 尝试从本地路径加载
    for path in possible_paths[:-1]:  # 排除最后一个URL路径
        if os.path.exists(path):
            return path, "local"
    
    # 如果本地没有找到，尝试从网络下载
    try:
        url = possible_paths[-1]
        response = requests.get(url, stream=True, timeout=30)
        if response.status_code == 200:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            file_name = "中国上市企业数字化转型指数（2007-2020）(1).xlsx"
            temp_path = os.path.join(temp_dir, file_name)
            
            # 写入临时文件
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path, "downloaded"
    except Exception as e:
        st.error(f"从网络下载数据文件失败: {e}")
    
    # 如果所有尝试都失败，返回None
    return None, None

# 加载数据
@st.cache_data
def load_data():
    # 查找数据文件
    file_path, source_type = find_data_file()
    
    if file_path is None:
        st.markdown("""
        <div class="error-message">
            <h3>数据文件未找到</h3>
            <p>系统无法找到数据文件"中国上市企业数字化转型指数（2007-2020）(1).xlsx"。</p>
            <p>请尝试以下解决方案：</p>
            <ol>
                <li>确保数据文件存在于以下位置之一：
                    <ul>
                        <li>当前工作目录</li>
                        <li>uploaded_files目录</li>
                        <li>使用下面的文件上传功能上传文件</li>
                    </ul>
                </li>
                <li>检查网络连接，系统会尝试从网络下载数据文件</li>
                <li>如果问题仍然存在，请联系系统管理员</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        return None
    
    try:
        # 加载数据
        df = pd.read_excel(file_path)
        
        # 显示加载成功信息
        if source_type == "local":
            st.success(f"已从本地路径成功加载数据文件: {file_path}，数据包含 {df.shape[0]} 行记录")
        elif source_type == "downloaded":
            st.success(f"已从网络成功下载数据文件并加载，数据包含 {df.shape[0]} 行记录，临时文件位置: {file_path}")
        
        return df
    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            <h3>数据加载失败</h3>
            <p>尝试加载数据文件时发生错误: {e}</p>
            <p>请尝试使用下面的文件上传功能上传正确的数据文件</p>
        </div>
        """, unsafe_allow_html=True)
        return None

# 数据预处理
@st.cache_data
def preprocess_data(df):
    if df is None:
        return None
    
    try:
        # 处理缺失值
        df = df.fillna(0)
        
        # 确保数值类型正确
        numeric_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用', '数字化转型']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # 添加企业类型标签
        df['企业类型'] = df.apply(lambda x: '高科技国企' if (x['高科技与否'] == 1 and x['国企与否'] == 1) else
                                      '高科技民企' if (x['高科技与否'] == 1 and x['国企与否'] == 0) else
                                      '传统国企' if (x['高科技与否'] == 0 and x['国企与否'] == 1) else
                                      '传统民企', axis=1)
        
        # 计算技术多样性（使用的技术种类数）
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术']
        available_tech_cols = [col for col in tech_cols if col in df.columns]
        if available_tech_cols:
            df['技术种类数'] = df[available_tech_cols].apply(lambda x: sum(x > 0), axis=1)
        else:
            df['技术种类数'] = 0
        
        # 计算年度增长率（需要按企业分组计算）
        if '证券代码' in df.columns and '年份' in df.columns and '数字化转型' in df.columns:
            df = df.sort_values(['证券代码', '年份'])
            df['年度增长率'] = df.groupby('证券代码')['数字化转型'].pct_change() * 100
            df['年度增长率'] = df['年度增长率'].fillna(0).replace([np.inf, -np.inf], 0)
        else:
            df['年度增长率'] = 0
        
        return df
    except Exception as e:
        st.error(f"数据预处理失败: {e}")
        return None

# 获取筛选选项
@st.cache_data
def get_filter_options(df):
    if df is None:
        return {
            'years': [],
            'industries': [],
            'provinces': [],
            'companies': []
        }
    
    try:
        years = sorted(df['年份'].unique()) if '年份' in df.columns else []
        industries = sorted(df['行业名称'].unique()) if '行业名称' in df.columns else []
        provinces = sorted(df['省份'].unique()) if '省份' in df.columns else []
        companies = sorted(df['股票简称'].unique()) if '股票简称' in df.columns else []
        
        return {
            'years': years,
            'industries': industries,
            'provinces': provinces,
            'companies': companies
        }
    except Exception as e:
        st.error(f"获取筛选选项失败: {e}")
        return {
            'years': [],
            'industries': [],
            'provinces': [],
            'companies': []
        }

# 筛选数据
def filter_data(df, filters):
    if df is None:
        return pd.DataFrame()
    
    try:
        filtered_df = df.copy()
        
        if filters['start_year'] and filters['end_year'] and '年份' in df.columns:
            filtered_df = filtered_df[(filtered_df['年份'] >= filters['start_year']) & 
                                      (filtered_df['年份'] <= filters['end_year'])]
        
        if filters['industry'] and filters['industry'] != '全部' and '行业名称' in df.columns:
            filtered_df = filtered_df[filtered_df['行业名称'] == filters['industry']]
        
        if filters['province'] and filters['province'] != '全部' and '省份' in df.columns:
            filtered_df = filtered_df[filtered_df['省份'] == filters['province']]
        
        if filters['company'] and filters['company'] != '全部' and '股票简称' in df.columns:
            filtered_df = filtered_df[filtered_df['股票简称'] == filters['company']]
        
        if filters['high_tech'] != '全部' and '高科技与否' in df.columns:
            high_tech_value = 1 if filters['high_tech'] == '是' else 0
            filtered_df = filtered_df[filtered_df['高科技与否'] == high_tech_value]
        
        if filters['soe'] != '全部' and '国企与否' in df.columns:
            soe_value = 1 if filters['soe'] == '是' else 0
            filtered_df = filtered_df[filtered_df['国企与否'] == soe_value]
        
        if filters['min_transform'] and '数字化转型' in df.columns:
            filtered_df = filtered_df[filtered_df['数字化转型'] >= filters['min_transform']]
        
        if filters['max_transform'] and '数字化转型' in df.columns:
            filtered_df = filtered_df[filtered_df['数字化转型'] <= filters['max_transform']]
        
        if filters['keyword']:
            keyword = filters['keyword'].lower()
            name_match = pd.Series([False]*len(filtered_df))
            industry_match = pd.Series([False]*len(filtered_df))
            
            if '股票简称' in df.columns:
                name_match = filtered_df['股票简称'].str.lower().str.contains(keyword, na=False)
            
            if '行业名称' in df.columns:
                industry_match = filtered_df['行业名称'].str.lower().str.contains(keyword, na=False)
            
            filtered_df = filtered_df[name_match | industry_match]
        
        return filtered_df
    except Exception as e:
        st.error(f"数据筛选失败: {e}")
        return pd.DataFrame()

# 创建统计指标卡片
def render_metric_cards(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_companies = df['股票简称'].nunique() if '股票简称' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #1E88E5; margin-bottom: 5px;">企业总数</h3>
                <h2 style="margin: 0;">{total_companies}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_transform = df['数字化转型'].mean() if '数字化转型' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #43A047; margin-bottom: 5px;">平均转型指数</h3>
                <h2 style="margin: 0;">{avg_transform:.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            max_transform = df['数字化转型'].max() if '数字化转型' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #FB8C00; margin-bottom: 5px;">最高转型指数</h3>
                <h2 style="margin: 0;">{max_transform}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            if '高科技与否' in df.columns and '股票简称' in df.columns:
                high_tech_count = df[df['高科技与否'] == 1]['股票简称'].nunique()
                total_count = df['股票简称'].nunique()
                high_tech_ratio = high_tech_count / total_count * 100 if total_count > 0 else 0
            else:
                high_tech_ratio = 0
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #8E24AA; margin-bottom: 5px;">高科技企业占比</h3>
                <h2 style="margin: 0;">{high_tech_ratio:.2f}%</h2>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"渲染统计指标失败: {e}")

# 创建行业分布图
def render_industry_distribution(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("行业分布")
        
        # 统计各行业企业数量
        if '行业名称' in df.columns and '股票简称' in df.columns:
            industry_counts = df.groupby('行业名称')['股票简称'].nunique().sort_values(ascending=False).head(10)
            
            fig = px.bar(
                x=industry_counts.index,
                y=industry_counts.values,
                labels={'x': '行业', 'y': '企业数量'},
                color=industry_counts.values,
                color_continuous_scale='Blues'
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=30, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少必要的列（行业名称或股票简称）")
    except Exception as e:
        st.error(f"渲染行业分布图失败: {e}")

# 创建地区分布图
def render_region_distribution(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("地区分布")
        
        # 统计各省企业数量
        if '省份' in df.columns and '股票简称' in df.columns:
            province_counts = df.groupby('省份')['股票简称'].nunique().sort_values(ascending=False).head(10)
            
            fig = px.pie(
                values=province_counts.values,
                names=province_counts.index,
                hole=0.4
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少必要的列（省份或股票简称）")
    except Exception as e:
        st.error(f"渲染地区分布图失败: {e}")

# 创建年度趋势图
def render_year_trend(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("年度数字化转型趋势")
        
        # 按年份统计平均转型指数
        if '年份' in df.columns and '数字化转型' in df.columns:
            year_trend = df.groupby('年份')['数字化转型'].mean().reset_index()
            
            fig = px.line(
                year_trend,
                x='年份',
                y='数字化转型',
                markers=True,
                labels={'年份': '年份', '数字化转型': '平均转型指数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少必要的列（年份或数字化转型）")
    except Exception as e:
        st.error(f"渲染年度趋势图失败: {e}")

# 创建技术分布雷达图
def render_tech_radar(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("技术应用分布")
        
        # 计算各项技术的平均值
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
        available_tech_cols = [col for col in tech_cols if col in df.columns]
        
        if available_tech_cols:
            tech_avg = df[available_tech_cols].mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatterpolar(
                r=tech_avg.values,
                theta=tech_avg.index,
                fill='toself',
                name='平均技术应用指数'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, tech_avg.max() * 1.2]
                    )),
                height=400,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少技术相关列")
    except Exception as e:
        st.error(f"渲染技术分布雷达图失败: {e}")

# 创建企业类型对比图
def render_company_type_comparison(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("企业类型对比")
        
        # 按企业类型统计平均转型指数
        if '企业类型' in df.columns and '数字化转型' in df.columns:
            type_comparison = df.groupby('企业类型')['数字化转型'].mean().reset_index()
            
            fig = px.bar(
                type_comparison,
                x='企业类型',
                y='数字化转型',
                color='企业类型',
                labels={'企业类型': '企业类型', '数字化转型': '平均转型指数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少必要的列（企业类型或数字化转型）")
    except Exception as e:
        st.error(f"渲染企业类型对比图失败: {e}")

# 创建企业详情表格
def render_company_details(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("企业详情")
        
        # 选择要显示的列
        display_columns = []
        rename_dict = {}
        
        # 检查并添加可用列
        if '证券代码' in df.columns:
            display_columns.append('证券代码')
            rename_dict['证券代码'] = '证券代码'
        
        if '股票简称' in df.columns:
            display_columns.append('股票简称')
            rename_dict['股票简称'] = '股票简称'
        
        if '年份' in df.columns:
            display_columns.append('年份')
            rename_dict['年份'] = '年份'
        
        if '行业名称' in df.columns:
            display_columns.append('行业名称')
            rename_dict['行业名称'] = '行业'
        
        if '省份' in df.columns:
            display_columns.append('省份')
            rename_dict['省份'] = '省份'
        
        if '城市' in df.columns:
            display_columns.append('城市')
            rename_dict['城市'] = '城市'
        
        if '高科技与否' in df.columns:
            display_columns.append('高科技与否')
            rename_dict['高科技与否'] = '高科技企业'
        
        if '国企与否' in df.columns:
            display_columns.append('国企与否')
            rename_dict['国企与否'] = '国有企业'
        
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
        for col in tech_cols:
            if col in df.columns:
                display_columns.append(col)
                rename_dict[col] = col
        
        if '数字化转型' in df.columns:
            display_columns.append('数字化转型')
            rename_dict['数字化转型'] = '数字化转型指数'
        
        if '技术种类数' in df.columns:
            display_columns.append('技术种类数')
            rename_dict['技术种类数'] = '技术种类数'
        
        if '年度增长率' in df.columns:
            display_columns.append('年度增长率')
            rename_dict['年度增长率'] = '年度增长率(%)'
        
        if not display_columns:
            st.warning("数据中没有可显示的列")
            return
        
        # 准备显示数据
        display_df = df[display_columns].copy()
        display_df = display_df.rename(columns=rename_dict)
        
        # 转换布尔值为文字
        if '高科技企业' in display_df.columns:
            display_df['高科技企业'] = display_df['高科技企业'].apply(lambda x: '是' if x == 1 else '否')
        
        if '国有企业' in display_df.columns:
            display_df['国有企业'] = display_df['国有企业'].apply(lambda x: '是' if x == 1 else '否')
        
        # 格式化年度增长率
        if '年度增长率(%)' in display_df.columns:
            display_df['年度增长率(%)'] = display_df['年度增长率(%)'].apply(lambda x: f"{x:.2f}%")
        
        # 按股票简称和年份排序
        if '股票简称' in display_df.columns and '年份' in display_df.columns:
            display_df = display_df.sort_values(['股票简称', '年份'])
        
        # 显示表格
        st.dataframe(display_df, use_container_width=True)
    except Exception as e:
        st.error(f"渲染企业详情表格失败: {e}")

# 创建企业详情页面
def render_company_detail_page(df, company_name):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.title(f"企业详情: {company_name}")
        
        # 获取该企业的所有年份数据
        if '股票简称' in df.columns:
            company_data = df[df['股票简称'] == company_name].sort_values('年份')
        else:
            st.warning("数据中缺少股票简称列")
            return
        
        if company_data.empty:
            st.warning("未找到该企业的数据")
            return
        
        # 显示企业基本信息
        with st.expander("企业基本信息", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if '证券代码' in company_data.columns:
                    st.metric("证券代码", company_data.iloc[0]['证券代码'])
            
            with col2:
                if '行业名称' in company_data.columns:
                    st.metric("行业", company_data.iloc[0]['行业名称'])
            
            with col3:
                if '省份' in company_data.columns:
                    st.metric("省份", company_data.iloc[0]['省份'])
            
            with col4:
                if '城市' in company_data.columns:
                    st.metric("城市", company_data.iloc[0]['城市'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                if '高科技与否' in company_data.columns:
                    high_tech = "是" if company_data.iloc[0]['高科技与否'] == 1 else "否"
                    st.metric("高科技企业", high_tech)
            
            with col2:
                if '国企与否' in company_data.columns:
                    soe = "是" if company_data.iloc[0]['国企与否'] == 1 else "否"
                    st.metric("国有企业", soe)
        
        # 显示企业年度转型趋势
        st.subheader("年度转型趋势")
        
        if '年份' in company_data.columns and '数字化转型' in company_data.columns:
            fig = px.line(
                company_data,
                x='年份',
                y='数字化转型',
                markers=True,
                labels={'年份': '年份', '数字化转型': '数字化转型指数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少必要的列（年份或数字化转型）")
        
        # 显示企业技术使用情况
        st.subheader("技术使用情况")
        
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
        available_tech_cols = [col for col in tech_cols if col in company_data.columns]
        
        if available_tech_cols and '年份' in company_data.columns:
            tech_data = company_data[available_tech_cols + ['年份']].melt(id_vars=['年份'], var_name='技术类型', value_name='使用指数')
            
            fig = px.bar(
                tech_data,
                x='年份',
                y='使用指数',
                color='技术类型',
                barmode='group',
                labels={'年份': '年份', '使用指数': '使用指数', '技术类型': '技术类型'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少技术相关列或年份列")
        
        # 显示企业技术种类数趋势
        st.subheader("技术种类数趋势")
        
        if '年份' in company_data.columns and '技术种类数' in company_data.columns:
            fig = px.line(
                company_data,
                x='年份',
                y='技术种类数',
                markers=True,
                labels={'年份': '年份', '技术种类数': '技术种类数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少技术种类数列或年份列")
        
        # 显示企业年度增长率趋势
        st.subheader("年度增长率趋势")
        
        if '年份' in company_data.columns and '年度增长率' in company_data.columns:
            fig = px.line(
                company_data,
                x='年份',
                y='年度增长率',
                markers=True,
                labels={'年份': '年份', '年度增长率': '年度增长率(%)'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少年度增长率列或年份列")
        
        # 显示企业详细数据表格
        st.subheader("详细数据")
        
        # 选择要显示的列
        display_columns = []
        rename_dict = {}
        
        if '年份' in company_data.columns:
            display_columns.append('年份')
            rename_dict['年份'] = '年份'
        
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
        for col in tech_cols:
            if col in company_data.columns:
                display_columns.append(col)
                rename_dict[col] = col
        
        if '数字化转型' in company_data.columns:
            display_columns.append('数字化转型')
            rename_dict['数字化转型'] = '数字化转型指数'
        
        if '技术种类数' in company_data.columns:
            display_columns.append('技术种类数')
            rename_dict['技术种类数'] = '技术种类数'
        
        if '年度增长率' in company_data.columns:
            display_columns.append('年度增长率')
            rename_dict['年度增长率'] = '年度增长率(%)'
        
        if not display_columns:
            st.warning("数据中没有可显示的列")
            return
        
        display_df = company_data[display_columns].copy()
        display_df = display_df.rename(columns=rename_dict)
        
        # 格式化年度增长率
        if '年度增长率(%)' in display_df.columns:
            display_df['年度增长率(%)'] = display_df['年度增长率(%)'].apply(lambda x: f"{x:.2f}%")
        
        st.dataframe(display_df, use_container_width=True)
    except Exception as e:
        st.error(f"渲染企业详情页面失败: {e}")

# 创建行业对比页面
def render_industry_comparison_page(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.title("行业对比分析")
        
        # 获取所有行业
        if '行业名称' in df.columns:
            industries = sorted(df['行业名称'].unique())
        else:
            st.warning("数据中缺少行业名称列")
            return
        
        # 选择要对比的行业
        selected_industries = st.multiselect(
            "选择要对比的行业",
            industries,
            default=industries[:5] if len(industries) >= 5 else industries
        )
        
        if not selected_industries:
            st.warning("请至少选择一个行业")
            return
        
        # 筛选数据
        industry_data = df[df['行业名称'].isin(selected_industries)]
        
        # 行业平均转型指数对比
        st.subheader("行业平均转型指数对比")
        
        if '数字化转型' in industry_data.columns:
            industry_avg = industry_data.groupby('行业名称')['数字化转型'].mean().reset_index()
            industry_avg = industry_avg.sort_values('数字化转型', ascending=False)
            
            fig = px.bar(
                industry_avg,
                x='行业名称',
                y='数字化转型',
                color='行业名称',
                labels={'行业名称': '行业', '数字化转型': '平均转型指数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=30, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少数字化转型列")
        
        # 行业年度趋势对比
        st.subheader("行业年度趋势对比")
        
        if '年份' in industry_data.columns and '数字化转型' in industry_data.columns:
            industry_year_trend = industry_data.groupby(['行业名称', '年份'])['数字化转型'].mean().reset_index()
            
            fig = px.line(
                industry_year_trend,
                x='年份',
                y='数字化转型',
                color='行业名称',
                markers=True,
                labels={'年份': '年份', '数字化转型': '平均转型指数', '行业名称': '行业'}
            )
            
            fig.update_layout(
                height=400,
                xaxis=dict(tickmode='linear'),
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少年份或数字化转型列")
        
        # 行业技术应用对比
        st.subheader("行业技术应用对比")
        
        tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
        available_tech_cols = [col for col in tech_cols if col in industry_data.columns]
        
        if available_tech_cols and '行业名称' in industry_data.columns:
            industry_tech = industry_data.groupby('行业名称')[available_tech_cols].mean().reset_index()
            
            # 创建子图
            fig = make_subplots(
                rows=1, cols=len(available_tech_cols),
                subplot_titles=available_tech_cols,
                horizontal_spacing=0.05
            )
            
            for i, tech in enumerate(available_tech_cols):
                fig.add_trace(
                    go.Bar(
                        x=industry_tech['行业名称'],
                        y=industry_tech[tech],
                        name=tech,
                        showlegend=False
                    ),
                    row=1, col=i+1
                )
            
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=50, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少技术相关列或行业名称列")
        
        # 行业技术种类数对比
        st.subheader("行业技术种类数对比")
        
        if '技术种类数' in industry_data.columns and '行业名称' in industry_data.columns:
            industry_tech_count = industry_data.groupby('行业名称')['技术种类数'].mean().reset_index()
            industry_tech_count = industry_tech_count.sort_values('技术种类数', ascending=False)
            
            fig = px.bar(
                industry_tech_count,
                x='行业名称',
                y='技术种类数',
                color='行业名称',
                labels={'行业名称': '行业', '技术种类数': '平均技术种类数'}
            )
            
            fig.update_layout(
                height=400,
                xaxis_tickangle=-45,
                margin=dict(l=20, r=20, t=30, b=80)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("数据中缺少技术种类数列或行业名称列")
    except Exception as e:
        st.error(f"渲染行业对比页面失败: {e}")

# 创建PDF导出功能（移除图表导出，确保不报错）
def create_pdf_report(df, include_overview=True, include_details=True):
    if df is None or df.empty:
        return None
    
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_path = tmp_file.name
        
        # 创建PDF文档
        doc = SimpleDocTemplate(tmp_path, pagesize=A4)
        story = []
        
        # 添加样式
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # 居中
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # 添加标题
        title = Paragraph("企业数字化转型数据分析报告", title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # 添加生成时间
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_para = Paragraph(f"生成时间: {date_str}", styles['Normal'])
        story.append(date_para)
        story.append(Spacer(1, 12))
        
        # 添加筛选条件说明
        filter_note = Paragraph("报告基于当前筛选条件生成，包含以下数据维度：", styles['Normal'])
        story.append(filter_note)
        story.append(Spacer(1, 12))
        
        # 添加概览统计
        if include_overview:
            story.append(Paragraph("概览统计", heading_style))
            story.append(Spacer(1, 12))
            
            # 计算统计数据
            total_companies = df['股票简称'].nunique() if '股票简称' in df.columns else 0
            avg_transform = df['数字化转型'].mean() if '数字化转型' in df.columns else 0
            max_transform = df['数字化转型'].max() if '数字化转型' in df.columns else 0
            
            if '高科技与否' in df.columns and '股票简称' in df.columns:
                high_tech_count = df[df['高科技与否'] == 1]['股票简称'].nunique()
                total_count = df['股票简称'].nunique()
                high_tech_ratio = high_tech_count / total_count * 100 if total_count > 0 else 0
            else:
                high_tech_ratio = 0
            
            # 创建统计表格
            data = [
                ['统计指标', '数值'],
                ['企业总数', str(total_companies)],
                ['平均转型指数', f"{avg_transform:.2f}"],
                ['最高转型指数', f"{max_transform:.2f}"],
                ['高科技企业占比', f"{high_tech_ratio:.2f}%"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 20))
        
        # 添加详细数据（移除图表部分）
        if include_details:
            story.append(Paragraph("详细数据", heading_style))
            story.append(Spacer(1, 12))
            
            # 选择要显示的列
            display_columns = []
            rename_dict = {}
            
            # 检查并添加可用列
            if '证券代码' in df.columns:
                display_columns.append('证券代码')
                rename_dict['证券代码'] = '证券代码'
            
            if '股票简称' in df.columns:
                display_columns.append('股票简称')
                rename_dict['股票简称'] = '股票简称'
            
            if '年份' in df.columns:
                display_columns.append('年份')
                rename_dict['年份'] = '年份'
            
            if '行业名称' in df.columns:
                display_columns.append('行业名称')
                rename_dict['行业名称'] = '行业'
            
            if '省份' in df.columns:
                display_columns.append('省份')
                rename_dict['省份'] = '省份'
            
            if '城市' in df.columns:
                display_columns.append('城市')
                rename_dict['城市'] = '城市'
            
            if '高科技与否' in df.columns:
                display_columns.append('高科技与否')
                rename_dict['高科技与否'] = '高科技企业'
            
            if '国企与否' in df.columns:
                display_columns.append('国企与否')
                rename_dict['国企与否'] = '国有企业'
            
            tech_cols = ['人工智能技术', '大数据技术', '云计算技术', '区块链技术', '数字技术运用']
            for col in tech_cols:
                if col in df.columns:
                    display_columns.append(col)
                    rename_dict[col] = col
            
            if '数字化转型' in df.columns:
                display_columns.append('数字化转型')
                rename_dict['数字化转型'] = '数字化转型指数'
            
            if '技术种类数' in df.columns:
                display_columns.append('技术种类数')
                rename_dict['技术种类数'] = '技术种类数'
            
            if '年度增长率' in df.columns:
                display_columns.append('年度增长率')
                rename_dict['年度增长率'] = '年度增长率(%)'
            
            if not display_columns:
                story.append(Paragraph("数据中没有可显示的列", styles['Normal']))
            else:
                # 准备显示数据
                display_df = df[display_columns].copy()
                display_df = display_df.rename(columns=rename_dict)
                
                # 转换布尔值为文字
                if '高科技企业' in display_df.columns:
                    display_df['高科技企业'] = display_df['高科技企业'].apply(lambda x: '是' if x == 1 else '否')
                
                if '国有企业' in display_df.columns:
                    display_df['国有企业'] = display_df['国有企业'].apply(lambda x: '是' if x == 1 else '否')
                
                # 格式化年度增长率
                if '年度增长率(%)' in display_df.columns:
                    display_df['年度增长率(%)'] = display_df['年度增长率(%)'].apply(lambda x: f"{x:.2f}%")
                
                # 按股票简称和年份排序
                if '股票简称' in display_df.columns and '年份' in display_df.columns:
                    display_df = display_df.sort_values(['股票简称', '年份'])
                
                # 限制数据量，避免PDF过大
                max_rows = 200
                if len(display_df) > max_rows:
                    display_df = display_df.head(max_rows)
                    story.append(Paragraph(f"注意: 由于数据量较大，仅显示前{max_rows}条记录", styles['Normal']))
                    story.append(Spacer(1, 12))
                
                # 创建数据表格
                data = [list(display_df.columns)]
                for _, row in display_df.iterrows():
                    data.append(list(row))
                
                # 调整表格样式以适应PDF
                table = Table(data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                ]))
                
                story.append(table)
        
        # 构建PDF
        doc.build(story)
        
        return tmp_path
    except Exception as e:
        st.error(f"创建PDF报告失败: {e}")
        # 清理临时文件
        if 'tmp_path' in locals():
            try:
                os.unlink(tmp_path)
            except:
                pass
        return None

# 渲染PDF导出功能
def render_pdf_export(df):
    if df is None or df.empty:
        st.warning("没有可用的数据")
        return
    
    try:
        st.subheader("导出PDF报告")
        
        # 选择要包含在报告中的内容
        include_overview = st.checkbox("包含概览统计", value=True)
        include_details = st.checkbox("包含详细数据", value=True)
        
        # 生成PDF按钮
        if st.button("生成PDF报告", type="primary"):
            with st.spinner("正在生成PDF报告，请稍候..."):
                try:
                    # 生成PDF（移除图表参数）
                    pdf_path = create_pdf_report(df, include_overview, include_details)
                    
                    if pdf_path is None:
                        st.error("PDF报告生成失败")
                        return
                    
                    # 读取PDF文件
                    with open(pdf_path, "rb") as f:
                        pdf_bytes = f.read()
                    
                    # 提供下载链接
                    st.success("[表情] PDF报告生成成功！")
                    st.download_button(
                        label="[表情] 下载PDF报告",
                        data=pdf_bytes,
                        file_name=f"企业数字化转型数据分析报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # 删除临时文件
                    try:
                        os.unlink(pdf_path)
                    except:
                        pass
                except Exception as e:
                    st.error(f"生成PDF报告时出错: {e}")
    except Exception as e:
        st.error(f"渲染PDF导出功能失败: {e}")

# 文件上传功能
def render_file_upload():
    st.subheader("上传数据文件")
    
    st.markdown("""
    <div class="file-upload-container">
        <p>如果系统无法自动找到数据文件，请上传Excel格式的数据文件</p>
        <p>文件名应为: 中国上市企业数字化转型指数（2007-2020）(1).xlsx</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "选择Excel文件",
        type=["xlsx", "xls"],
        help="请上传Excel格式的数据文件",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # 保存上传的文件
            upload_dir = "uploaded_files"
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            file_path = os.path.join(upload_dir, "中国上市企业数字化转型指数（2007-2020）(1).xlsx")
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"文件已保存到: {file_path}，请刷新页面以加载新上传的数据")
            
            # 添加刷新按钮
            if st.button("[表情] 刷新页面"):
                st.rerun()
        except Exception as e:
            st.error(f"文件上传失败，错误信息: {e}，请检查文件格式并重试")

# 主函数
def main():
    # 尝试加载数据
    df = load_data()
    
    # 如果数据加载失败，显示文件上传功能
    if df is None:
        render_file_upload()
        return
    
    # 数据预处理
    df = preprocess_data(df)
    
    if df is None:
        st.error("数据预处理失败")
        return
    
    # 获取筛选选项
    filter_options = get_filter_options(df)
    
    # 页面标题
    st.markdown('<h1 class="main-header">企业数字化转型数据查询系统</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">基于中国上市企业数字化转型指数（2007-2020）</p>', unsafe_allow_html=True)
    
    # 创建页面内的筛选器
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.subheader("数据筛选")
    
    # 筛选器布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 年份范围筛选
        if filter_options['years']:
            min_year = min(filter_options['years'])
            max_year = max(filter_options['years'])
            selected_year_range = st.slider(
                "年份范围",
                min_value=min_year,
                max_value=max_year,
                value=(min_year, max_year)
            )
        else:
            selected_year_range = (None, None)
        
        # 行业筛选
        if filter_options['industries']:
            selected_industry = st.selectbox(
                "行业",
                ["全部"] + filter_options['industries']
            )
        else:
            selected_industry = "全部"
    
    with col2:
        # 省份筛选
        if filter_options['provinces']:
            selected_province = st.selectbox(
                "省份",
                ["全部"] + filter_options['provinces']
            )
        else:
            selected_province = "全部"
        
        # 高科技企业筛选
        high_tech_options = ["全部", "是", "否"]
        selected_high_tech = st.selectbox(
            "高科技企业",
            high_tech_options
        )
    
    with col3:
        # 企业筛选（可选）
        if filter_options['companies'] and len(filter_options['companies']) < 1000:  # 避免选项过多
            selected_company = st.selectbox(
                "企业",
                ["全部"] + filter_options['companies']
            )
        else:
            selected_company = "全部"
        
        # 国有企业筛选
        soe_options = ["全部", "是", "否"]
        selected_soe = st.selectbox(
            "国有企业",
            soe_options
        )
    
    # 额外筛选条件
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        # 转型指数范围筛选
        if '数字化转型' in df.columns:
            min_transform = st.number_input(
                "转型指数最小值",
                min_value=0.0,
                value=0.0,
                step=0.1
            )
        else:
            min_transform = 0
    
    with col2:
        if '数字化转型' in df.columns:
            max_transform = st.number_input(
                "转型指数最大值",
                min_value=0.0,
                value=float(df['数字化转型'].max()),
                step=0.1
            )
        else:
            max_transform = 0
    
    with col3:
        # 关键词搜索
        keyword = st.text_input("关键词搜索", placeholder="输入企业名称或行业关键词")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 构建筛选条件
    filters = {
        'start_year': selected_year_range[0],
        'end_year': selected_year_range[1],
        'industry': selected_industry,
        'province': selected_province,
        'company': selected_company,
        'high_tech': selected_high_tech,
        'soe': selected_soe,
        'min_transform': min_transform,
        'max_transform': max_transform,
        'keyword': keyword
    }
    
    # 应用筛选
    filtered_df = filter_data(df, filters)
    
    # 显示筛选结果数量（修复：使用st.markdown替代st.info的unsafe_allow_html参数）
    total_records = filtered_df.shape[0]
    total_companies = filtered_df['股票简称'].nunique() if '股票简称' in filtered_df.columns else 0
    
    st.markdown(f"""
    <div class="info-message">
        筛选结果: 共 {total_records} 条记录, {total_companies} 家企业
    </div>
    """, unsafe_allow_html=True)
    
    # 创建页面导航（使用tabs替代侧边栏）
    tab1, tab2, tab3, tab4 = st.tabs(["[表情] 数据概览", "[表情] 企业详情", "[表情] 行业对比", "[表情] 数据导出"])
    
    with tab1:
        # 显示统计指标卡片
        render_metric_cards(filtered_df)
        
        # 显示图表
        col1, col2 = st.columns(2)
        
        with col1:
            render_industry_distribution(filtered_df)
        
        with col2:
            render_region_distribution(filtered_df)
        
        render_year_trend(filtered_df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_tech_radar(filtered_df)
        
        with col2:
            render_company_type_comparison(filtered_df)
        
        # 显示企业详情表格
        render_company_details(filtered_df)
    
    with tab2:
        # 选择企业
        if filter_options['companies']:
            company_options = ["请选择企业"] + sorted(filtered_df['股票简称'].unique()) if '股票简称' in filtered_df.columns else ["请选择企业"]
            selected_company_detail = st.selectbox("选择企业查看详情", company_options)
            
            if selected_company_detail != "请选择企业":
                render_company_detail_page(df, selected_company_detail)
        else:
            st.warning("数据中没有企业信息")
    
    with tab3:
        render_industry_comparison_page(df)
    
    with tab4:
        render_pdf_export(filtered_df)

# 运行主函数
if __name__ == "__main__":
    main()
