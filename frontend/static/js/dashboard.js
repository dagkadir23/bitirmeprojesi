/**
 * dashboard.js - SecureVision AI Dashboard İstemci Tarafı Mantığı
 * 
 * Gerçek zamanlı istatistik güncelleme, log akışı, raporlama,
 * siber güvenlik kontrolleri ve hava durumu widget'ı.
 */

// ==========================================
// GLOBAL DEĞİŞKENLER
// ==========================================

// UserRole sunucu tarafından HTML'e enjekte edilir
// const UserRole = "{{ role }}"; -- dashboard.html'de tanımlanır

let allReports = [];

// ==========================================
// SİBER GÜVENLİK KONTROL FONKSİYONLARI
// ==========================================

async function toggleAction(type) {
    if (UserRole !== 'admin') {
        alert("Yetkisiz Erişim!");
        return;
    }
    await fetch(`/api/toggle_${type}`, { method: 'POST' });
}

async function verifyLogs() {
    if (UserRole !== 'admin') return;
    const res = await fetch('/api/verify_logs', { method: 'POST' });
    const data = await res.json();
    const el = document.getElementById('integrity-status');
    el.textContent = data.status;

    if (data.status.includes("Başarısız")) {
        el.className = "block text-center text-[10px] font-bold px-2 py-2 rounded mb-2 bg-red-500 text-white animate-pulse";
    } else {
        el.className = "block text-center text-[10px] font-bold px-2 py-2 rounded mb-2 bg-emerald-600 text-white";
    }
}

async function poisonLog() {
    if (UserRole !== 'admin') return;
    await fetch('/api/poison_log', { method: 'POST' });
    verifyLogs();
}

// ==========================================
// İSTATİSTİK GÜNCELLEME
// ==========================================

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        const data = await response.json();

        // Metrikler
        document.getElementById('total-anomalies').textContent = data.stats.total_anomalies;
        document.getElementById('processing-time').textContent = data.metrics.processing_time;
        document.getElementById('accuracy-display').textContent = '%' + data.metrics.accuracy;
        document.getElementById('f1-display').textContent = data.metrics.f1_score;
        document.getElementById('far-display').textContent = data.metrics.false_alarm_rate;
        document.getElementById('cpu-display').textContent = data.metrics.cpu_usage;

        // Canlı Log Akışı
        const logsContainer = document.getElementById('live-logs-container');
        if (data.logs && data.logs.length > 0) {
            logsContainer.innerHTML = data.logs.map(log => {
                const isManipulated = log.message.includes("MANİPÜLASYONU");
                return `<div class="py-0.5 border-b border-slate-800/30 ${isManipulated ? 'text-red-400 animate-pulse bg-red-900/10' : ''}">
                    <span class="text-slate-500 mr-1">[${log.time}]</span>
                    <span class="text-slate-600 mr-1" title="Hash: ${log.hash}">[${log.hash}]</span>
                    <span class="${isManipulated ? 'text-red-400 font-bold' : 'text-emerald-400'}">${log.message}</span>
                </div>`;
            }).join('');
        }

        // Video çerçevesi renk değişimi
        const videoWrapper = document.getElementById('video-wrapper');
        if (data.stats.current_status === "Risk Tespit Edildi") {
            videoWrapper.classList.add('anim-pulse-red');
            videoWrapper.style.borderColor = 'rgba(239, 68, 68, 0.8)';
        } else {
            videoWrapper.classList.remove('anim-pulse-red');
            videoWrapper.style.borderColor = 'rgba(56, 189, 248, 0.4)';
        }

        // Admin buton durumları
        if (UserRole === 'admin') {
            const btnAtm = document.getElementById('btn-attack');
            if (data.state.is_attack_active) {
                btnAtm.className = "bg-red-600 text-white py-2 rounded text-xs font-bold transition";
            } else {
                btnAtm.className = "bg-red-900/50 text-red-200 py-2 rounded text-xs font-bold transition";
            }

            const btnDef = document.getElementById('btn-defense');
            if (data.state.is_defense_active) {
                btnDef.className = "bg-emerald-600 text-white py-2 rounded text-xs font-bold transition";
            } else {
                btnDef.className = "bg-emerald-900/50 text-emerald-200 py-2 rounded text-xs font-bold transition";
            }
        }

    } catch (e) {
        // Sessiz hata (bağlantı kopması durumunda)
    }
}

// ==========================================
// RAPORLAMA
// ==========================================

async function fetchReports() {
    try {
        const res = await fetch('/api/reports');
        const data = await res.json();
        allReports = data.reports || [];
        renderReports();
    } catch (e) {
        // Sessiz hata
    }
}

function renderReports() {
    const filterDate = document.getElementById('dateFilter').value;
    const tbody = document.getElementById('reports-body');

    let filtered = allReports;
    if (filterDate) {
        filtered = allReports.filter(r => r.date === filterDate);
    }

    if (filtered.length > 0) {
        tbody.innerHTML = filtered.map(r => `
            <tr class="hover:bg-slate-800/60 transition border-b border-slate-700/50">
                <td class="px-4 py-3 font-mono text-[10px] text-blue-400">#${r.id}</td>
                <td class="px-4 py-3 text-xs text-slate-300">${r.date} ${r.start}</td>
                <td class="px-4 py-3">
                    <span class="bg-slate-700/50 border border-slate-600 px-2 py-1 rounded text-[10px] font-medium ${r.behavior.includes('Perturbation') ? 'text-red-400 border-red-900' : 'text-slate-300'}">
                        ${r.behavior}
                    </span>
                </td>
                <td class="px-4 py-3 text-xs text-slate-300">${r.duration} sn</td>
                <td class="px-4 py-3 text-xs font-bold text-orange-400">${r.max_score}</td>
                <td class="px-4 py-3 text-[9px] font-mono text-slate-500 text-right">
                    <i class="fa-solid fa-lock text-slate-600 mr-1"></i>${r.hash}
                </td>
            </tr>
        `).join('');
    } else {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-500 text-xs">
            Arşivde gösterilecek vaka bulunmamaktadır veya filtrelenen tarihte kayıt yoktur.
        </td></tr>`;
    }
}

// ==========================================
// TEHDİT İSTİHBARATI WİDGET'I (CVE)
// ==========================================

async function fetchThreatIntel() {
    try {
        const res = await fetch('/api/threats');
        const data = await res.json();

        const container = document.getElementById('threat-widget-content');
        if (container && data && data.threats) {
            if (data.threats.length === 0) {
                container.innerHTML = `<p class="text-[10px] text-slate-500 text-center py-4">Aktif tehdit kaydı bulunamadı.</p>`;
            } else {
                container.innerHTML = data.threats.map(threat => {
                    let badgeColor = "bg-red-500/20 text-red-400 border-red-500/30";
                    if (threat.cvss_score < 7.0) {
                        badgeColor = "bg-amber-500/20 text-amber-400 border-amber-500/30";
                    } else if (threat.cvss_score < 4.0) {
                        badgeColor = "bg-blue-500/20 text-blue-400 border-blue-500/30";
                    }

                    return `
                        <div class="bg-slate-800/40 border border-slate-700/40 rounded-lg p-2 hover:border-red-500/30 transition">
                            <div class="flex justify-between items-start mb-1">
                                <span class="text-[10px] font-bold text-slate-200 font-mono">${threat.cve_id}</span>
                                <span class="border px-1.5 py-0.5 rounded text-[8px] font-semibold tracking-wide ${badgeColor}">
                                    CVSS ${threat.cvss_score.toFixed(1)}
                                </span>
                            </div>
                            <p class="text-[9px] text-slate-400 leading-normal mb-1">
                                ${threat.description}
                            </p>
                            <div class="flex justify-between text-[8px] text-slate-500 font-mono">
                                <span>Kaynak: ${threat.source || 'NIST'}</span>
                                <span>Etiket: ${threat.keyword}</span>
                            </div>
                        </div>
                    `;
                }).join('');
            }

            const sourceEl = document.getElementById('threat-source');
            if (sourceEl) {
                sourceEl.textContent = data.source || 'NIST NVD';
            }

            const timeEl = document.getElementById('threat-time');
            if (timeEl) {
                timeEl.textContent = data.timestamp || '--:--:--';
            }
        }
    } catch (e) {
        // Sessiz hata
    }
}

// ==========================================
// BAŞLATMA
// ==========================================

document.addEventListener('DOMContentLoaded', function () {
    // Tarih filtresi
    const dateFilter = document.getElementById('dateFilter');
    if (dateFilter) {
        dateFilter.addEventListener('change', renderReports);
    }

    // Periyodik güncelleme
    setInterval(fetchStats, 1000);
    setInterval(fetchReports, 2000);

    // Tehdit istihbaratını başlangıçta çek, sonra 10 dakikada bir güncelle
    fetchThreatIntel();
    setInterval(fetchThreatIntel, 600000);
});
