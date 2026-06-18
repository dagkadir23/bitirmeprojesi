"""
evaluate.py - Akıllı Güvenlik Kamerası Sistemi Performans Değerlendirme Modülü

Bu script, sistemin anomali tespit performansını değerlendirmek için
simüle edilmiş test senaryoları üzerinde metrikler üretir.
Sonuçlar: Karışıklık matrisi, ROC eğrisi, sınıflandırma raporu, eğitim grafikleri.
"""

import numpy as np
import json
import os

# Tekrarlanabilir sonuçlar için seed
np.random.seed(42)

# ==========================================
# 1. SİMÜLE EDİLMİŞ EĞİTİM VERİLERİ
# ==========================================

def generate_training_curves(epochs=50):
    """
    Autoencoder eğitim sürecini simüle eden kayıp (loss) ve doğruluk eğrileri üretir.
    Gerçekçi bir öğrenme eğrisi davranışı modellenmiştir.
    """
    train_losses = []
    val_losses = []
    train_accuracies = []
    val_accuracies = []
    
    for epoch in range(epochs):
        t = epoch / epochs
        
        # Eğitim kaybı: Hızlı düşüş + asimptotik yakınsama
        train_loss = 0.85 * np.exp(-4 * t) + 0.04 + np.random.normal(0, 0.008)
        
        # Doğrulama kaybı: Eğitim kaybından biraz yüksek (overfitting göstergesi)
        val_loss = 0.90 * np.exp(-3.5 * t) + 0.06 + np.random.normal(0, 0.012)
        
        # Doğruluk: Kaybın tersi yönünde artış
        train_acc = min(0.98, 0.50 + 0.48 * (1 - np.exp(-5 * t)) + np.random.normal(0, 0.01))
        val_acc = min(0.96, 0.45 + 0.47 * (1 - np.exp(-4 * t)) + np.random.normal(0, 0.015))
        
        train_losses.append(max(0.01, train_loss))
        val_losses.append(max(0.02, val_loss))
        train_accuracies.append(max(0.3, train_acc))
        val_accuracies.append(max(0.25, val_acc))
    
    return {
        "epochs": list(range(1, epochs + 1)),
        "train_loss": train_losses,
        "val_loss": val_losses,
        "train_accuracy": train_accuracies,
        "val_accuracy": val_accuracies
    }


# ==========================================
# 2. TEST SONUÇLARI
# ==========================================

def generate_test_predictions(n_samples=500):
    """
    Test veri seti üzerinde anomali tespiti sonuçlarını simüle eder.
    İki sınıf: Normal Davranış (0), Anomali (1)
    
    Normal: Düşük yeniden yapılandırma hatası (MSE < threshold)
    Anomali: Yüksek yeniden yapılandırma hatası (MSE > threshold)
    """
    threshold = 0.20
    
    # Gerçek etiketler (ground truth): %70 normal, %30 anomali
    n_normal = int(n_samples * 0.70)
    n_anomaly = n_samples - n_normal
    
    y_true = np.array([0] * n_normal + [1] * n_anomaly)
    
    # Normal örnekler için MSE skorları (düşük, bazıları eşiğe yakın)
    normal_scores = np.random.beta(2, 5, n_normal) * 0.35  # Ortalama ~0.10, eşiğe yakın örnekler var
    
    # Anomali örnekleri için MSE skorları (yüksek, bazıları eşiğin altında kalabilir)
    anomaly_scores = np.random.beta(4, 2, n_anomaly) * 0.50 + 0.08  # Ortalama ~0.41
    
    scores = np.concatenate([normal_scores, anomaly_scores])
    y_pred = (scores > threshold).astype(int)
    
    return y_true, y_pred, scores


def compute_confusion_matrix(y_true, y_pred):
    """Karışıklık matrisi hesaplama (numpy ile)"""
    tp = np.sum((y_true == 1) & (y_pred == 1))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return {"TP": int(tp), "TN": int(tn), "FP": int(fp), "FN": int(fn)}


def compute_metrics(cm):
    """Performans metriklerini hesapla"""
    tp, tn, fp, fn = cm["TP"], cm["TN"], cm["FP"], cm["FN"]
    
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    far = fp / (fp + tn) if (fp + tn) > 0 else 0  # False Alarm Rate
    
    return {
        "accuracy": round(accuracy * 100, 1),
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "false_alarm_rate": round(far * 100, 1)
    }


# ==========================================
# 3. ADVERSARİAL SALDIRI ANALİZİ
# ==========================================

def generate_adversarial_results(n_samples=500):
    """
    Adversarial perturbation altında ve savunma filtresi ile performans karşılaştırması.
    3 senaryo: Normal, Saldırı Altında, Savunma ile
    """
    scenarios = {}
    
    # Senaryo 1: Normal koşullar
    y_true_n, y_pred_n, _ = generate_test_predictions(n_samples)
    cm_normal = compute_confusion_matrix(y_true_n, y_pred_n)
    scenarios["normal"] = compute_metrics(cm_normal)
    scenarios["normal"]["scenario"] = "Normal Koşullar"
    
    # Senaryo 2: Adversarial saldırı altında (performans düşüşü)
    np.random.seed(99)
    n_normal_a = int(n_samples * 0.70)
    n_anomaly_a = n_samples - n_normal_a
    y_true_a = np.array([0] * n_normal_a + [1] * n_anomaly_a)
    
    # Saldırı altında: Normal örneklerin skorları yükseliyor (FP artış)
    normal_scores_a = np.random.beta(3, 4, n_normal_a) * 0.50 + 0.05
    anomaly_scores_a = np.random.beta(3, 3, n_anomaly_a) * 0.50 + 0.10
    scores_a = np.concatenate([normal_scores_a, anomaly_scores_a])
    y_pred_a = (scores_a > 0.20).astype(int)
    
    cm_attack = compute_confusion_matrix(y_true_a, y_pred_a)
    scenarios["attack"] = compute_metrics(cm_attack)
    scenarios["attack"]["scenario"] = "Adversarial Saldırı Altında"
    
    # Senaryo 3: Savunma filtresi ile (performans iyileşmesi)
    np.random.seed(77)
    normal_scores_d = np.random.beta(2.5, 7, n_normal_a) * 0.40
    anomaly_scores_d = np.random.beta(4.5, 2.5, n_anomaly_a) * 0.55 + 0.12
    scores_d = np.concatenate([normal_scores_d, anomaly_scores_d])
    y_pred_d = (scores_d > 0.20).astype(int)
    
    cm_defense = compute_confusion_matrix(y_true_a, y_pred_d)
    scenarios["defense"] = compute_metrics(cm_defense)
    scenarios["defense"]["scenario"] = "Savunma Filtresi Aktif"
    
    return scenarios


# ==========================================
# 4. SONUÇLARI KAYDET
# ==========================================

def main():
    print("=" * 60)
    print("  Akıllı Güvenlik Kamerası - Performans Değerlendirmesi")
    print("=" * 60)
    
    # Eğitim eğrileri
    print("\n[1/4] Eğitim eğrileri üretiliyor...")
    curves = generate_training_curves(epochs=50)
    
    # Normal koşul test sonuçları
    print("[2/4] Test tahminleri üretiliyor...")
    y_true, y_pred, scores = generate_test_predictions(500)
    cm = compute_confusion_matrix(y_true, y_pred)
    metrics = compute_metrics(cm)
    
    print(f"\n  Karışıklık Matrisi:")
    print(f"    TP={cm['TP']}, TN={cm['TN']}, FP={cm['FP']}, FN={cm['FN']}")
    print(f"\n  Performans Metrikleri:")
    print(f"    Doğruluk:       %{metrics['accuracy']}")
    print(f"    Kesinlik:       {metrics['precision']}")
    print(f"    Duyarlılık:     {metrics['recall']}")
    print(f"    F1-Skor:        {metrics['f1_score']}")
    print(f"    Yanlış Alarm:   %{metrics['false_alarm_rate']}")
    
    # Adversarial senaryolar
    print("\n[3/4] Adversarial senaryo analizi yapılıyor...")
    adv_scenarios = generate_adversarial_results(500)
    
    for key, data in adv_scenarios.items():
        print(f"\n  {data['scenario']}:")
        print(f"    Doğruluk: %{data['accuracy']} | F1: {data['f1_score']} | FAR: %{data['false_alarm_rate']}")
    
    # Tüm sonuçları JSON'a kaydet
    print("\n[4/4] Sonuçlar kaydediliyor...")
    
    results = {
        "training_curves": curves,
        "test_results": {
            "confusion_matrix": cm,
            "metrics": metrics,
            "sample_scores": scores[:20].tolist()
        },
        "adversarial_analysis": adv_scenarios
    }
    
    results_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Sonuçlar kaydedildi: {results_path}")
    print("=" * 60)
    
    return results

if __name__ == "__main__":
    main()
