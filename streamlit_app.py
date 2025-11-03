import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import io

# ---------------- 页面配置 ----------------
st.set_page_config(page_title="Flower Poster — Streamlit", layout="centered")

FIGSIZE = (6, 8)
DPI = 100

# ---------------- 配色与形状 ----------------
def flower_palette():
    """清新配色（与你原始代码一致）"""
    return [
        (0.95, 0.75, 0.80),  # 粉色
        (0.70, 0.85, 0.70),  # 嫩绿
        (0.70, 0.80, 0.95),  # 淡蓝
        (0.85, 0.75, 0.95),  # 浅紫
        (0.98, 0.93, 0.75)   # 米黄
    ]

def dreamy_purple_palette(k=8):
    """梦幻紫系备用（可在侧边栏选择）"""
    hues = np.linspace(0.70, 0.85, k)
    cols = []
    for h in hues:
        # hls_to_rgb: 用 H, L, S（这里用明亮度高、饱和度中偏低）
        import colorsys
        s = np.random.uniform(0.25, 0.45)
        l = np.random.uniform(0.72, 0.86)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        cols.append((r, g, b))
    return cols

def hex_to_rgb01(hexstr: str):
    hexstr = hexstr.lstrip("#")
    return tuple(int(hexstr[i:i+2], 16)/255.0 for i in (0, 2, 4))

def flower_shape(center=(0.5, 0.5), r=0.3, petals=6, petal_factor=0.3, points=400):
    """生成花瓣形状 (玫瑰曲线)"""
    theta = np.linspace(0, 2*np.pi, points)
    radii = r * (1 + petal_factor * np.cos(petals * theta))
    x = center[0] + radii * np.cos(theta)
    y = center[1] + radii * np.sin(theta)
    return x, y

# ---------------- 绘制函数（不调用 plt.show） ----------------
def draw_flower_poster_3d(
    n_layers=6,
    petals=6,
    size_min=0.15, size_max=0.35,
    petal_factor_min=0.2, petal_factor_max=0.4,
    bg_color="#FAFAF7",
    with_shadow=True,
    shadow_ratio=0.08,
    gradient_steps=5,
    alpha_start=0.2, alpha_step=0.15,
    palette_name="fresh",
    seed=42
):
    random.seed(int(seed))
    np.random.seed(int(seed))

    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    ax.set_facecolor(hex_to_rgb01(bg_color))
    ax.axis('off')

    if palette_name == "fresh":
        palette = flower_palette()
    else:
        palette = dreamy_purple_palette(max(8, n_layers))

    for _ in range(n_layers):
        cx, cy = random.random(), random.random()
        rr = random.uniform(size_min, size_max)
        petal_factor = random.uniform(petal_factor_min, petal_factor_max)

        if with_shadow:
            shadow_offset = rr * shadow_ratio
            x_shadow, y_shadow = flower_shape(center=(cx + shadow_offset, cy - shadow_offset),
                                              r=rr, petals=petals, petal_factor=petal_factor)
            ax.fill(x_shadow, y_shadow, color=(0, 0, 0, 0.15), edgecolor='none')

        x, y = flower_shape(center=(cx, cy), r=rr, petals=petals, petal_factor=petal_factor)
        color = random.choice(palette)

        # 径向渐变：多层透明填充模拟
        for k in range(gradient_steps):
            alpha = alpha_start + alpha_step * k
            scale = 1 - 0.05 * k
            x_scaled = cx + (x - cx) * scale
            y_scaled = cy + (y - cy) * scale
            ax.fill(x_scaled, y_scaled, color=color, alpha=alpha, edgecolor='none')

    ax.text(0.05, 0.95, "Flower Poster", fontsize=18, weight='bold', transform=ax.transAxes)
    ax.text(0.05, 0.91, "Fresh Colors • Petal Shapes • 3D Effect", fontsize=11, transform=ax.transAxes)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    fig.tight_layout(pad=0)
    return fig

# ---------------- Streamlit UI ----------------
st.title("🌸 Flower Poster — Streamlit")
st.caption("Fresh colors • Rose curves • Layered gradient petals • PNG export")

# 左侧控制区
seed = st.sidebar.number_input("Random Seed", min_value=0, max_value=10_000_000, value=42, step=1)
n_layers = st.sidebar.slider("Number of Flowers (layers)", 2, 30, 8)
petals = st.sidebar.slider("Petal Count", 3, 16, 6)
size_min, size_max = st.sidebar.slider("Flower Size Range", 0.08, 0.50, (0.15, 0.35))
petal_factor_min, petal_factor_max = st.sidebar.slider("Petal Factor Range", 0.05, 0.60, (0.20, 0.40))

palette_choice = st.sidebar.selectbox("Palette", ["fresh (pink/green/blue/purple/cream)", "dreamy purple"])
palette_key = "fresh" if palette_choice.startswith("fresh") else "purple"

bg_color = st.sidebar.color_picker("Background Color", value="#FAFAF7")
with_shadow = st.sidebar.checkbox("Soft Shadow", value=True)
gradient_steps = st.sidebar.slider("Gradient Steps", 1, 8, 5)
alpha_start = st.sidebar.slider("Gradient Alpha Start", 0.0, 0.5, 0.20, 0.01)
alpha_step = st.sidebar.slider("Gradient Alpha Step", 0.05, 0.35, 0.15, 0.01)

# 生成与展示
fig = draw_flower_poster_3d(
    n_layers=int(n_layers),
    petals=int(petals),
    size_min=float(size_min), size_max=float(size_max),
    petal_factor_min=float(petal_factor_min), petal_factor_max=float(petal_factor_max),
    bg_color=bg_color,
    with_shadow=with_shadow,
    gradient_steps=int(gradient_steps),
    alpha_start=float(alpha_start),
    alpha_step=float(alpha_step),
    palette_name=("fresh" if palette_key == "fresh" else "purple"),
    seed=int(seed)
)

st.pyplot(fig)

# 下载 PNG
buf = io.BytesIO()
fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", pad_inches=0)
st.download_button(
    "Download PNG",
    data=buf.getvalue(),
    file_name=f"flower_poster_seed{int(seed)}.png",
    mime="image/png",
)
