/**
 * landing.js - SecureVision AI Landing Page Animasyonları
 * 
 * Scroll reveal, smooth scrolling ve sayaç animasyonları.
 */

// ==========================================
// SCROLL REVEAL ANİMASYONLARI
// ==========================================

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
        if (entry.isIntersecting) {
            entry.target.style.transitionDelay = '0.1s';
            setTimeout(() => {
                entry.target.classList.add('visible');
            }, 100);
        }
    });
}, {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
});

document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

// ==========================================
// SMOOTH SCROLL
// ==========================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
