# app.py - 首页（介绍 + 二维码 + 页面链接）
import streamlit as st
import qrcode
from PIL import Image
import io
import os

st.set_page_config(page_title="统一入口 - 三个分析页面", layout="wide")

st.markdown("<h1 style='text-align:center;color:#1E88E5;'>统一入口 · 三个分析页面</h1>", unsafe_allow_html=True)

st.markdown("""
- 本系统包含三套独立的 Streamlit 页面（每个页面保留你原来的代码，未作修改）。
- 请选择左侧或顶部的页面导航进入对应页面：
  1. 企业数字化转型数据查询系统（第1份代码）
  2. 企业数字化转型数据查询分析系统（第2份代码）
  3. 企业ESG量化数据查询分析系统（第3份代码）
""")

st.markdown("---")
st.header("如何访问（二维码）")

# 允许通过环境变量定制 app 地址（部署时设置真实 URL）
app_url = os.environ.get("APP_URL", "http://localhost:8501")
st.write("二维码默认指向：", app_url)
st.write("说明：如果你把 app 部署到公网（Streamlit Cloud / 含域名的服务器 / ngrok），请将 `APP_URL` 环境变量设为公网地址，然后刷新此页面生成指向公网的二维码。")

# 生成二维码
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
qr.add_data(app_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

buf = io.BytesIO()
img.save(buf, format="PNG")
buf.seek(0)

col1, col2 = st.columns([1,2])
with col1:
    st.image(buf, width=220)
    st.caption("扫码打开该 Streamlit 应用（默认 localhost:8501）")
with col2:
    st.markdown("**快捷操作**")
    st.markdown("- 本地运行：在项目根运行 `streamlit run app.py`")
    st.markdown("- 如果要让外网可访问，可使用 `ngrok` 或部署到 Streamlit Cloud，并把公网地址写入 `APP_URL` 环境变量。")
    st.markdown("- 页面位于 `pages/` 下，Streamlit 多页面会自动生成导航。")

st.markdown("---")
st.markdown("如果需要，我可以：\n\n- 帮你把三份代码自动写入 `pages/` 目录（我会保留原始内容不改）。\n- 或帮你生成一个可直接部署到 Streamlit Cloud 的仓库结构并把二维码指向部署后的公网地址。")