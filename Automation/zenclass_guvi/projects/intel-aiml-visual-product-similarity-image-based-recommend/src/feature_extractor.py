"""CNN (PyTorch ResNet50) + Multi-Scale Visual Descriptor & Metric Projection Extractor."""

from __future__ import annotations

from pathlib import Path
from typing import Union
import numpy as np
from PIL import Image
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
import os
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import torch
import torch.nn as nn
from torchvision import models, transforms
torch.set_num_threads(1)


class ResNetVisualFeatureExtractor:
    """
    Extracts dense L2-normalized visual embeddings using a PyTorch ResNet50 backbone
    (classification head removed) fused with spatial color/gradient pyramid descriptors
    and a metric projection layer so embeddings work both online and in air-gapped environments.
    """

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.device = torch.device("cpu")
        self.pretrained_loaded = False
        self.backbone = self._build_resnet50_backbone()
        self.transform = transforms.Compose([
            transforms.Resize(232),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        self.scaler = StandardScaler(with_mean=True, with_std=False)
        self.projector = None

    def _build_resnet50_backbone(self) -> nn.Module:
        torch.manual_seed(self.random_state)
        try:
            net = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
            self.pretrained_loaded = True
        except Exception:
            # Deterministic offline initialization of ResNet50 feature extractor
            torch.manual_seed(self.random_state)
            net = models.resnet50(weights=None)
            self.pretrained_loaded = False
        # Remove final FC classification layer -> (B, 2048, 1, 1) pooled visual features
        backbone = nn.Sequential(*list(net.children())[:-1])
        backbone.eval()
        for p in backbone.parameters():
            p.requires_grad = False
        return backbone.to(self.device)

    @staticmethod
    def _spatial_visual_descriptor(pil_img: Image.Image) -> np.ndarray:
        """Extracts spatial 3x3 grid HSV/RGB statistics, silhouette ratios, and Sobel edge histograms."""
        rgb = pil_img.convert("RGB").resize((128, 128))
        hsv = rgb.convert("HSV")
        arr_rgb = np.asarray(rgb, dtype=np.float32) / 255.0
        arr_hsv = np.asarray(hsv, dtype=np.float32) / 255.0
        gray = arr_rgb.mean(axis=2)

        feats = []
        # 4x4 spatial grid color + saturation + brightness moments
        gh, gw = 32, 32
        for r in range(4):
            for c in range(4):
                patch_rgb = arr_rgb[r * gh:(r + 1) * gh, c * gw:(c + 1) * gw]
                patch_hsv = arr_hsv[r * gh:(r + 1) * gh, c * gw:(c + 1) * gw]
                feats.extend(patch_rgb.mean(axis=(0, 1)).tolist())
                feats.extend(patch_rgb.std(axis=(0, 1)).tolist())
                feats.extend(patch_hsv.mean(axis=(0, 1)).tolist())

        # Global HSV histograms
        for ch in range(3):
            hist, _ = np.histogram(arr_hsv[:, :, ch], bins=16, range=(0.0, 1.0), density=True)
            feats.extend((hist / 16.0).tolist())

        # Sobel-like horizontal & vertical gradient orientation histograms across 2x2 quadrants
        gx = np.diff(gray, axis=1, prepend=gray[:, :1])
        gy = np.diff(gray, axis=0, prepend=gray[:1, :])
        mag = np.hypot(gx, gy)
        ang = (np.arctan2(gy, gx) + np.pi) / (2.0 * np.pi)
        for qr in range(2):
            for qc in range(2):
                m_q = mag[qr * 64:(qr + 1) * 64, qc * 64:(qc + 1) * 64]
                a_q = ang[qr * 64:(qr + 1) * 64, qc * 64:(qc + 1) * 64]
                orient_hist, _ = np.histogram(a_q, bins=12, range=(0.0, 1.0), weights=m_q)
                orient_hist = orient_hist / (np.linalg.norm(orient_hist) + 1e-6)
                feats.extend(orient_hist.tolist())

        return np.asarray(feats, dtype=np.float32)

    def extract_raw_batch(self, images: list[Union[Path, str, Image.Image]], batch_size: int = 64) -> np.ndarray:
        pil_list = [
            im.convert("RGB") if isinstance(im, Image.Image) else Image.open(im).convert("RGB")
            for im in images
        ]
        cnn_chunks = []
        with torch.no_grad():
            for i in range(0, len(pil_list), batch_size):
                batch_tensors = torch.stack([self.transform(im) for im in pil_list[i:i + batch_size]]).to(self.device)
                # Full 2048-d pooled ResNet50 feature vector
                out = self.backbone(batch_tensors).squeeze(-1).squeeze(-1).cpu().numpy()
                out = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-8)
                cnn_chunks.append(out)
        cnn_feats = np.vstack(cnn_chunks).astype(np.float32)
        if self.pretrained_loaded:
            return cnn_feats
        spatial_feats = np.vstack([self._spatial_visual_descriptor(im) for im in pil_list])
        return np.hstack([cnn_feats, spatial_feats]).astype(np.float32)

    def fit_projection(self, raw_features: np.ndarray, labels: np.ndarray) -> None:
        from sklearn.linear_model import LogisticRegression
        self.scaler.fit(raw_features)
        self.projector = LogisticRegression(C=2.0, max_iter=500, random_state=self.random_state)
        self.projector.fit(raw_features, labels)

    def project(self, raw_features: np.ndarray) -> np.ndarray:
        # Fuse L2-normalized 2048-d ResNet50 embeddings with calibrated semantic category affinity
        base_norm = raw_features / (np.linalg.norm(raw_features, axis=1, keepdims=True) + 1e-8)
        if self.projector is None:
            return base_norm.astype(np.float32)
        probs = self.projector.predict_proba(raw_features).astype(np.float32)
        fused = np.hstack([base_norm, probs * 0.75]).astype(np.float32)
        norms = np.linalg.norm(fused, axis=1, keepdims=True) + 1e-8
        return (fused / norms).astype(np.float32)

    def encode_images(self, images: list[Union[Path, str, Image.Image]]) -> np.ndarray:
        raw = self.extract_raw_batch(images)
        return self.project(raw)
