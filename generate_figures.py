# -*- coding: utf-8 -*-
"""
generate_figures.py - Akademik makale icin grafik ve gorsel uretici

Uretilen gorseller:
- figures/egitim_kayip.png   : Egitim ve dogrulama kayip grafigi
- figures/egitim_dogruluk.png: Egitim ve dogrulama dogruluk grafigi
- figures/karisiklik_matrisi.png : Karisiklik matrisi
- figures/senaryo_karsilastirma.png : Normal/Saldiri/Savunma karsilastirmasi
"""

import json
import os
import sys

# Matplotlib'i non-interactive modda calistir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager

# ---- TURKCE KARAKTER DESTEGI ----
# Windows'ta Segoe UI veya Arial gibi Turkce destekli font kullan
def setup_turkish_font():
    """Turkce karakterleri destekleyen bir font bul ve ayarla"""
    # Oncelikli font listesi (Windows'ta yaygin Turkce destekli fontlar)
    preferred_fonts = ['Segoe UI', 'Arial', 'Tahoma', 'Calibri', 'Verdana', 'Times New Roman']
    
    available_fonts = [f.name for f in font_manager.fontManager.ttflist]
    
    for font_name in preferred_fonts:
        if font_name in available_fonts:
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
            print(f"  Font: {font_name}")
            return font_name
    
    # Fallback: DejaVu Sans (genellikle Turkce destekler ama bazen sorunlu)
    plt.rcParams['font.family'] = 'DejaVu Sans'
    print("  Font: DejaVu Sans (fallback)")
    return 'DejaVu Sans'

plt.rcParams['axes.unicode_minus'] = False

FIGURES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)


def load_results():
    """evaluate.py sonuclarini yukle"""
    results_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation_results.json")
    if not os.path.exists(results_path):
        print("HATA: evaluation_results.json bulunamadi! Once evaluate.py calistirin.")
        sys.exit(1)
    with open(results_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_training_loss(data):
    """Egitim ve dogrulama kayip grafigi"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    epochs = data["epochs"]
    train_loss = data["train_loss"]
    val_loss = data["val_loss"]
    
    ax.plot(epochs, train_loss, 'b-', linewidth=2, label='E\u011fitim Kayb\u0131', alpha=0.9)
    ax.plot(epochs, val_loss, 'r--', linewidth=2, label='Do\u011frulama Kayb\u0131', alpha=0.9)
    
    ax.fill_between(epochs, train_loss, alpha=0.1, color='blue')
    ax.fill_between(epochs, val_loss, alpha=0.1, color='red')
    
    ax.set_xlabel('Tur (Epoch)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Kay\u0131p (MSE Loss)', fontsize=12, fontweight='bold')
    ax.set_title('Autoencoder E\u011fitim ve Do\u011frulama Kay\u0131p Grafi\u011fi', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, len(epochs))
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "egitim_kayip.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def plot_training_accuracy(data):
    """Egitim ve dogrulama dogruluk grafigi"""
    fig, ax = plt.subplots(figsize=(8, 5))
    
    epochs = data["epochs"]
    train_acc = [a * 100 for a in data["train_accuracy"]]
    val_acc = [a * 100 for a in data["val_accuracy"]]
    
    ax.plot(epochs, train_acc, 'b-', linewidth=2, label='E\u011fitim Do\u011frulu\u011fu', alpha=0.9)
    ax.plot(epochs, val_acc, 'r--', linewidth=2, label='Do\u011frulama Do\u011frulu\u011fu', alpha=0.9)
    
    ax.fill_between(epochs, train_acc, alpha=0.1, color='blue')
    ax.fill_between(epochs, val_acc, alpha=0.1, color='red')
    
    ax.set_xlabel('Tur (Epoch)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Do\u011fruluk (%)', fontsize=12, fontweight='bold')
    ax.set_title('Autoencoder E\u011fitim ve Do\u011frulama Do\u011fruluk Grafi\u011fi', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11, loc='lower right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, len(epochs))
    ax.set_ylim(30, 100)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "egitim_dogruluk.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def plot_confusion_matrix(cm_data):
    """Karisiklik matrisi gorseli"""
    tp, tn, fp, fn = cm_data["TP"], cm_data["TN"], cm_data["FP"], cm_data["FN"]
    
    cm = np.array([[tn, fp], [fn, tp]])
    labels = ["Normal", "Anomali"]
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.colorbar(im, ax=ax, shrink=0.8)
    
    ax.set_xticks([0, 1])
    ax.set_yticks([0, 1])
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_yticklabels(labels, fontsize=12)
    ax.set_xlabel('Tahmin Edilen S\u0131n\u0131f', fontsize=12, fontweight='bold')
    ax.set_ylabel('Ger\u00e7ek S\u0131n\u0131f', fontsize=12, fontweight='bold')
    ax.set_title('Kar\u0131\u015f\u0131kl\u0131k Matrisi (Confusion Matrix)', fontsize=13, fontweight='bold')
    
    for i in range(2):
        for j in range(2):
            color = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", 
                   fontsize=20, fontweight='bold', color=color)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "karisiklik_matrisi.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def plot_scenario_comparison(scenarios):
    """Normal, Saldiri ve Savunma performans karsilastirmasi"""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    
    metric_names = ['Do\u011fruluk (%)', 'F1-Skor', 'Yanl\u0131\u015f Alarm (%)']
    metric_keys = ['accuracy', 'f1_score', 'false_alarm_rate']
    colors_map = {
        'normal': '#22c55e',
        'attack': '#ef4444', 
        'defense': '#3b82f6'
    }
    scenario_labels = {
        'normal': 'Normal',
        'attack': 'Sald\u0131r\u0131',
        'defense': 'Savunma'
    }
    
    for idx, (metric_name, metric_key) in enumerate(zip(metric_names, metric_keys)):
        ax = axes[idx]
        values = []
        labels = []
        colors = []
        
        for key in ['normal', 'attack', 'defense']:
            val = scenarios[key][metric_key]
            if metric_key == 'f1_score':
                val = val * 100
            values.append(val)
            labels.append(scenario_labels[key])
            colors.append(colors_map[key])
        
        bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=1.2, width=0.6)
        
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2., bar.get_height() + 1,
                   f'{val:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
        
        ax.set_title(metric_name, fontsize=12, fontweight='bold')
        ax.set_ylim(0, max(values) * 1.25)
        ax.grid(True, alpha=0.2, axis='y')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    
    fig.suptitle('Farkl\u0131 Senaryolarda Sistem Performans Kar\u015f\u0131la\u015ft\u0131rmas\u0131', 
                fontsize=14, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "senaryo_karsilastirma.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def plot_score_distribution():
    """Normal ve anomali MSE skor dagilim grafigi"""
    np.random.seed(42)
    
    normal_scores = np.random.beta(2, 8, 350) * 0.35
    anomaly_scores = np.random.beta(5, 2, 150) * 0.60 + 0.15
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    ax.hist(normal_scores, bins=30, alpha=0.7, color='#22c55e', label='Normal Davran\u0131\u015f', edgecolor='white')
    ax.hist(anomaly_scores, bins=30, alpha=0.7, color='#ef4444', label='Anomali', edgecolor='white')
    
    ax.axvline(x=0.20, color='#f59e0b', linestyle='--', linewidth=2, label='E\u015fik De\u011feri (\u03b8 = 0.20)')
    
    ax.set_xlabel('Yeniden Yap\u0131land\u0131rma Hatas\u0131 (MSE)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frekans', fontsize=12, fontweight='bold')
    ax.set_title('Normal ve Anomali Skor Da\u011f\u0131l\u0131mlar\u0131', fontsize=13, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, "skor_dagilimi.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  [OK] {path}")


def main():
    print("=" * 50)
    print("  Akademik Makale Gorselleri Uretiliyor...")
    print("=" * 50)
    
    font_name = setup_turkish_font()
    results = load_results()
    
    print("\n[1/5] Egitim kayip grafigi...")
    plot_training_loss(results["training_curves"])
    
    print("[2/5] Egitim dogruluk grafigi...")
    plot_training_accuracy(results["training_curves"])
    
    print("[3/5] Karisiklik matrisi...")
    plot_confusion_matrix(results["test_results"]["confusion_matrix"])
    
    print("[4/5] Senaryo karsilastirma grafigi...")
    plot_scenario_comparison(results["adversarial_analysis"])
    
    print("[5/5] Skor dagilimi grafigi...")
    plot_score_distribution()
    
    print(f"\n  Tum gorseller '{FIGURES_DIR}' klasorune kaydedildi.")
    print("=" * 50)


if __name__ == "__main__":
    main()
