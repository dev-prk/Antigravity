"""Builds rich e-commerce product metadata catalog over the 500 product images."""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
IMAGES_DIR = BASE_DIR / "data" / "images"
CATALOG_CSV = BASE_DIR / "data" / "catalog.csv"

BRAND_BY_CATEGORY = {
    "backpack": ["Wildcraft", "Skybags", "American Tourister", "Tommy Gear"],
    "bottle": ["Milton", "Cello", "Borosil", "HydroFlask"],
    "headphones": ["Sony", "boAt", "Sennheiser", "JBL"],
    "lamp": ["Philips", "Wipro", "Syska", "IKEA"],
    "laptop": ["Dell", "HP", "Lenovo", "ASUS"],
    "mug": ["Milton", "Borosil", "ClayCraft", "Chumbak"],
    "chair": ["Featherlite", "GreenSoul", "Wakefit", "Nilkamal"],
    "sneakers": ["Nike", "Adidas", "Puma", "New Balance"],
    "shoes": ["Nike", "Adidas", "Puma", "Skechers"],
    "sunglasses": ["Ray-Ban", "Fastrack", "Vincent Chase", "Oakley"],
    "tshirt": ["Levi's", "Allen Solly", "US Polo", "Roadster"],
    "watch": ["Titan", "Fossil", "Casio", "Timex"],
}

PRICE_BANDS = {
    "backpack": (899, 3499),
    "headphones": (1299, 14999),
    "lamp": (499, 2799),
    "laptop": (34999, 94999),
    "mug": (199, 799),
    "chair": (3499, 15999),
    "sneakers": (1799, 8999),
    "shoes": (1599, 7999),
    "sunglasses": (799, 6499),
    "tshirt": (399, 1899),
    "watch": (1499, 12999),
}


def build_or_load_catalog(images_dir: Path = IMAGES_DIR, catalog_csv: Path = CATALOG_CSV) -> pd.DataFrame:
    if catalog_csv.exists():
        df = pd.read_csv(catalog_csv)
        if len(df) > 0:
            return df

    rng = np.random.default_rng(2026)
    img_files = sorted([p for p in images_dir.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png"}])
    rows = []
    for idx, img_path in enumerate(img_files):
        stem_parts = img_path.stem.split("_")
        cat = stem_parts[0].lower()
        item_num = stem_parts[1] if len(stem_parts) > 1 else str(idx)
        brands = BRAND_BY_CATEGORY.get(cat, ["AmazonBasics", "UrbanEdge", "PrimeCraft"])
        brand = brands[idx % len(brands)]
        low_p, high_p = PRICE_BANDS.get(cat, (599, 4999))
        price = float(int(rng.integers(low_p, high_p)))
        rating = round(float(rng.uniform(3.6, 4.9)), 1)
        in_stock = bool(idx % 11 != 0)  # ~91% in stock

        rows.append({
            "product_id": f"PRD-{idx+1:04d}",
            "title": f"{brand} {cat.replace('-', ' ').title()} Series #{item_num}",
            "category": cat,
            "brand": brand,
            "price_inr": price,
            "rating": rating,
            "in_stock": in_stock,
            "filename": img_path.name,
            "image_rel_path": f"data/images/{img_path.name}",
        })

    df = pd.DataFrame(rows)
    catalog_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(catalog_csv, index=False)
    return df
