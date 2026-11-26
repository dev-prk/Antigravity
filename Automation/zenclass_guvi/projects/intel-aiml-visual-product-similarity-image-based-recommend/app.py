"""Amazon-Style Visual Product Similarity & Recommendation Streamlit App."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
from PIL import Image
import streamlit as st

from src.catalog import BASE_DIR
from src.vector_engine import VisualSearchEngine

st.set_page_config(
    page_title="Visual Product Similarity Engine",
    page_icon="🛍️",
    layout="wide",
)


@st.cache_resource(show_spinner="Initializing PyTorch ResNet50 embeddings & FAISS vector index...")
def get_engine() -> VisualSearchEngine:
    return VisualSearchEngine.load_or_build()


engine = get_engine()
catalog = engine.catalog
metrics = engine.metrics

st.sidebar.title("🛍️ Visual Search Filters")
top_k = st.sidebar.slider("Top-K Similar Products", min_value=4, max_value=16, value=8, step=2)
cat_options = sorted(catalog["category"].unique())
selected_cats = st.sidebar.multiselect("Filter Categories (Optional)", cat_options)
min_p, max_p = float(catalog["price_inr"].min()), float(catalog["price_inr"].max())
price_band = st.sidebar.slider("Price Range (₹)", min_value=min_p, max_value=max_p, value=(min_p, max_p))
min_rating = st.sidebar.slider("Minimum Rating (★)", 0.0, 4.8, 3.5, 0.1)
in_stock_only = st.sidebar.checkbox("In-Stock Items Only", value=False)

st.title("🛍️ Visual Product Similarity & Image-Based Recommendation System")
st.caption("PyTorch ResNet50 Feature Extraction • Dense Embedding Projection • Millisecond FAISS Cosine Search")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Indexed Products", f"{metrics['total_catalog_images']:,}")
m2.metric("Precision@1", f"{metrics['precision_at_1']*100:.1f}%")
m3.metric("Precision@5", f"{metrics['precision_at_5']*100:.1f}%")
m4.metric("Precision@10", f"{metrics['precision_at_10']*100:.1f}%")
m5.metric("FAISS Search Latency", f"{metrics['avg_faiss_latency_ms']:.3f} ms")

tab1, tab2, tab3 = st.tabs([
    "🔍 Visual Similarity Search (Amazon-Style)",
    "📈 Quantitative Evaluation (Precision@K & Recall@K)",
    "📦 Product Catalog Browser",
])

with tab1:
    mode = st.radio("Select Query Input Mode", ["Select Catalog Product", "Upload Custom Product Image"], horizontal=True)
    query_obj = None
    query_caption = ""
    query_img_display = None

    if mode == "Select Catalog Product":
        c1, c2 = st.columns([1, 2])
        q_cat = c1.selectbox("Browse Query Category", cat_options)
        cat_items = catalog[catalog["category"] == q_cat]
        q_pid = c2.selectbox(
            "Choose Query Product",
            cat_items["product_id"].tolist(),
            format_func=lambda pid: f"{pid} — {cat_items.loc[cat_items['product_id']==pid, 'title'].iloc[0]} (₹{cat_items.loc[cat_items['product_id']==pid, 'price_inr'].iloc[0]:.0f})",
        )
        q_row = catalog[catalog["product_id"] == q_pid].iloc[0]
        query_obj = q_pid
        query_img_display = Image.open(BASE_DIR / q_row["image_rel_path"])
        query_caption = f"{q_row['title']} | Category: {q_row['category']} | ₹{q_row['price_inr']:.0f} | ★{q_row['rating']}"
    else:
        uploaded = st.file_uploader("Upload a Product Photo (.jpg / .png)", type=["jpg", "jpeg", "png"])
        if uploaded is not None:
            pil_q = Image.open(uploaded).convert("RGB")
            query_obj = pil_q
            query_img_display = pil_q
            query_caption = f"Uploaded Query Image ({uploaded.name})"

    if query_obj is not None:
        left, right = st.columns([1, 3])
        with left:
            st.subheader("Query Item")
            st.image(query_img_display, caption=query_caption, use_container_width=True)

        with right:
            recs, lat_ms = engine.search(
                query=query_obj,
                top_k=top_k,
                categories=selected_cats or None,
                price_range=price_band,
                in_stock_only=in_stock_only,
                min_rating=min_rating,
            )
            st.subheader(f"Top-{len(recs)} Visually Similar Recommendations (FAISS Latency: {lat_ms:.3f} ms)")
            if recs.empty:
                st.warning("No matching products satisfied the active price/category/stock filters.")
            else:
                cols = st.columns(4)
                for idx, row in recs.iterrows():
                    with cols[idx % 4]:
                        img = Image.open(BASE_DIR / row["image_rel_path"])
                        st.image(img, use_container_width=True)
                        st.markdown(f"**{row['title']}**")
                        st.caption(
                            f"Match: **{row['cosine_similarity']*100:.1f}%** | `{row['category']}`\n\n"
                            f"**₹{row['price_inr']:.0f}** • ★{row['rating']} • {'✅ In Stock' if row['in_stock'] else '❌ Out of Stock'}"
                        )

with tab2:
    st.subheader("Out-of-Sample Retrieval Evaluation (20% Stratified Holdout Set)")
    cat_df = pd.DataFrame([
        {"Category": k, "Precision@5": v}
        for k, v in metrics["category_precision_at_5"].items()
    ])
    st.plotly_chart(
        px.bar(cat_df, x="Category", y="Precision@5", color="Precision@5", text_auto=".2f", title="Per-Category Visual Retrieval Precision@5"),
        use_container_width=True,
    )
    st.json(metrics)

with tab3:
    st.subheader(f"Indexed E-Commerce Catalog ({len(catalog):,} Items)")
    st.dataframe(catalog.drop(columns=["image_rel_path"]), use_container_width=True, hide_index=True)
