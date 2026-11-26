# Visual Product Similarity & Image-Based Recommendation System (Amazon-Style)

Computer-vision product recommendation engine using **PyTorch ResNet50** feature extraction, metric embedding projection, and **FAISS (`IndexFlatIP`)** approximate/exact cosine similarity search across **500 real e-commerce product images** spanning 10 categories.

## Architecture

```
Product Images (500 .jpg items across 10 categories) / Uploaded User Photo
        │
        ▼
  Visual Feature Extractor (src/feature_extractor.py)
  ├── PyTorch ResNet50 Backbone (classification head removed)
  ├── Spatial HSV/RGB & Sobel Gradient Orientation Descriptors
  └── L2-Normalized Dense Embedding Projection
        │
        ▼
  FAISS Cosine Similarity Index (models/visual_index.faiss)
        │
        ▼
  Metadata Ranking & Filter Layer (Category, Price ₹, Rating ★, In-Stock)
        │
        ▼
  Amazon-Style Streamlit Visual Search UI + Precision@K Benchmark (app.py)
```

## Quickstart

```bash
pip install -r requirements.txt
pytest -q
streamlit run app.py
```
