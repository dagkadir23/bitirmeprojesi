"""
external_api.py - Harici API Entegrasyonu

NIST NVD CVE API üzerinden güncel siber güvenlik açıklarını çekme.
Siber güvenlik ve akıllı kamera temasıyla entegre widget verisi sağlar.
"""

from flask import Blueprint, jsonify
import requests
import time

from backend.routes.auth import login_required
from backend.config import NVD_API_URL, NVD_API_KEY, NVD_CACHE_SECONDS, NVD_SEARCH_KEYWORDS
from backend.models import cache_cve_data, get_cached_cves

external_api_bp = Blueprint('external_api', __name__)

# Bellek içi cache kilit mekanizması
_last_fetch_time = 0

def fetch_cves_from_nvd():
    """NVD API'den CVE verilerini çeker ve veritabanına kaydeder."""
    headers = {}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY

    # NVD API key olmadan 6 saniyede bir istek yapılmasını önerir.
    # Bu yüzden her sorgulamada sadece tek bir keyword aratalım.
    # Dönüşümlü olarak keyword seçelim.
    current_keyword = NVD_SEARCH_KEYWORDS[int(time.time() // NVD_CACHE_SECONDS) % len(NVD_SEARCH_KEYWORDS)]

    try:
        params = {
            "keywordSearch": current_keyword,
            "resultsPerPage": 5
        }
        response = requests.get(NVD_API_URL, headers=headers, params=params, timeout=8)
        
        if response.status_code == 200:
            data = response.json()
            vulns = data.get("vulnerabilities", [])
            
            for item in vulns:
                cve_item = item.get("cve", {})
                cve_id = cve_item.get("id")
                source = cve_item.get("sourceIdentifier", "NVD")
                published_date = cve_item.get("published", "")
                
                # Tarih formatlama: 2023-03-24T15:15:12.120 -> 2023-03-24
                if published_date and "T" in published_date:
                    published_date = published_date.split("T")[0]
                
                # Açıklama bulma (İngilizce)
                description = "Açıklama bulunmuyor."
                descriptions = cve_item.get("descriptions", [])
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break
                
                # CVSS skoru ve önem derecesi
                cvss_score = 0.0
                severity = "UNKNOWN"
                
                metrics = cve_item.get("metrics", {})
                # CVSS v3.1 kontrolü
                if "cvssMetricV31" in metrics:
                    cvss_data = metrics["cvssMetricV31"][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = cvss_data.get("baseSeverity", "UNKNOWN")
                elif "cvssMetricV30" in metrics:
                    cvss_data = metrics["cvssMetricV30"][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = cvss_data.get("baseSeverity", "UNKNOWN")
                elif "cvssMetricV2" in metrics:
                    cvss_data = metrics["cvssMetricV2"][0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    severity = metrics["cvssMetricV2"][0].get("baseSeverity", "UNKNOWN")
                
                # Kaydet
                cache_cve_data(
                    cve_id=cve_id,
                    source=source,
                    published_date=published_date,
                    description=description,
                    cvss_score=cvss_score,
                    severity=severity,
                    keyword=current_keyword
                )
            return True
        return False
    except Exception as e:
        print(f"[NVD API Hatası] {e}")
        return False


def get_fallback_cves():
    """NVD API'ye erişilemezse sunulacak gerçekçi demo/fallback CVE listesi."""
    return [
        {
            "cve_id": "CVE-2021-36260",
            "source": "Hikvision",
            "published_date": "2021-09-18",
            "description": "Hikvision IP kameralarında web sunucusundaki girdi denetimi hatasından kaynaklanan Uzaktan Kod Çalıştırma (RCE) açığı.",
            "cvss_score": 9.8,
            "severity": "CRITICAL",
            "keyword": "surveillance camera",
            "is_fallback": True
        },
        {
            "cve_id": "CVE-2022-28060",
            "source": "Dahua",
            "published_date": "2022-05-10",
            "description": "Dahua IP kameralarında kimlik doğrulamayı atlayarak yetkisiz erişim elde edilmesine olanak tanıyan güvenlik açığı.",
            "cvss_score": 9.8,
            "severity": "CRITICAL",
            "keyword": "surveillance camera",
            "is_fallback": True
        },
        {
            "cve_id": "CVE-2020-11444",
            "source": "OpenCV",
            "published_date": "2020-04-02",
            "description": "OpenCV kütüphanesinde resim dosyaları ayrıştırılırken bellek taşması sonucu uygulamanın çökmesine yol açan açık.",
            "cvss_score": 7.8,
            "severity": "HIGH",
            "keyword": "OpenCV",
            "is_fallback": True
        },
        {
            "cve_id": "CVE-2023-28320",
            "source": "Hikvision",
            "published_date": "2023-04-12",
            "description": "Hikvision IP kameralarında ağ paketlerinin yanlış işlenmesiyle cihazın kilitlenmesine neden olan servis dışı bırakma (DoS) açığı.",
            "cvss_score": 7.5,
            "severity": "HIGH",
            "keyword": "surveillance camera",
            "is_fallback": True
        }
    ]


@external_api_bp.route('/api/threats')
@login_required
def get_threats():
    """
    Güvenlik açıkları (CVE) tehdit istihbaratı endpointi.
    Veritabanından önbelleğe alınmış verileri döner, süresi dolmuşsa API'den yeniler.
    """
    global _last_fetch_time
    current_time = time.time()

    # Önce DB'den son cache'i çekelim
    cves = get_cached_cves(max_age_seconds=NVD_CACHE_SECONDS)

    # Cache boş veya süresi geçmiş ise ve son sorgulamadan bu yana en az 10 saniye geçmişse (sıkışmayı önlemek için)
    if not cves and (current_time - _last_fetch_time > 10):
        _last_fetch_time = current_time
        success = fetch_cves_from_nvd()
        if success:
            cves = get_cached_cves(max_age_seconds=NVD_CACHE_SECONDS)

    # Hala veri yoksa (API hata verdi veya internet yok), fallback verilerini kullan
    if not cves:
        cves = get_fallback_cves()
        # Fallback verisini de DB'ye ekleyelim ki cache'lensin
        for c in cves:
            cache_cve_data(
                cve_id=c.get("cve_id"),
                source=c.get("source"),
                published_date=c.get("published_date"),
                description=c.get("description"),
                cvss_score=c.get("cvss_score"),
                severity=c.get("severity"),
                keyword=c.get("keyword")
            )
        # Yeniden çek
        cves = get_cached_cves(max_age_seconds=NVD_CACHE_SECONDS)

    # Eğer hala boşsa (SQL/DB hatası vb.) direkt listeyi dön
    if not cves:
        cves = get_fallback_cves()

    # UI'a uygun JSON şemasıyla geri dönüyoruz
    return jsonify({
        "status": "success",
        "threats": cves,
        "source": "NIST NVD API" if not any(c.get("is_fallback") for c in cves) else "Demo Veri Tabanı (Fallback)",
        "timestamp": time.strftime('%H:%M:%S')
    })
