/* ─── NAV SCROLL ─── */
window.addEventListener('scroll', () => {
  document.getElementById('navbar').classList.toggle('scrolled', scrollY > 50);
});

/* ─── MOBILE NAV ─── */
function openMob() { document.getElementById('mobileNav').classList.add('open'); }
function closeMob() { document.getElementById('mobileNav').classList.remove('open'); }

/* ─── SCROLL REVEAL ─── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('in');
      revealObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal,.reveal-left,.reveal-right').forEach(el => revealObserver.observe(el));

/* Stagger feature cards in grid */
document.querySelectorAll('.feat-grid').forEach(grid => {
  grid.querySelectorAll('.feat-card.reveal').forEach((card, i) => {
    card.style.transitionDelay = `${0.07 * i + 0.05}s`;
  });
});

/* ─── COUNT UP ─── */
function countUp(el) {
  const target = parseInt(el.dataset.count);
  const display = target >= 1000 ? target / 1000 : target;
  const suffix = target >= 1000 ? 'K+' : '+';
  let current = 0;
  const increment = display / 70;
  const timer = setInterval(() => {
    current += increment;
    if (current >= display) { current = display; clearInterval(timer); }
    el.textContent = Math.floor(current) + suffix;
  }, 16);
}
const countObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting && e.target.dataset.count) {
      countUp(e.target);
      countObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.5 });
document.querySelectorAll('[data-count]').forEach(el => countObserver.observe(el));

/* ─── RIPPLE EFFECT ─── */
function addRipple(e, el) {
  const rect = el.getBoundingClientRect();
  const size = Math.max(rect.width, rect.height) * 2;
  const x = e.clientX - rect.left - size / 2;
  const y = e.clientY - rect.top - size / 2;
  const ripple = document.createElement('span');
  ripple.className = 'ripple';
  ripple.style.cssText = `width:${size}px;height:${size}px;left:${x}px;top:${y}px`;
  el.appendChild(ripple);
  ripple.addEventListener('animationend', () => ripple.remove());
}

/* ─── TILT EFFECT on feature cards ─── */
document.querySelectorAll('.feat-card,.testi-card,.p-card').forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    card.style.transform = `translateY(-8px) scale(1.01) rotateY(${x * 6}deg) rotateX(${-y * 6}deg)`;
  });
  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
    card.style.transition = 'transform .5s cubic-bezier(.34,1.56,.64,1),box-shadow .3s,border-color .3s';
  });
  card.addEventListener('mouseenter', () => {
    card.style.transition = 'box-shadow .3s,border-color .3s';
  });
});

/* ─── BILLING TOGGLE ─── */
let annual = false;
const priceData = {
  us:  { m: '0.99', a: '0.83', note: '$9.99/yr · Save 17%' },
  ca:  { m: '1.99', a: '1.25', note: '$15/yr · Save 37%' },
  uk:  { m: '1.99', a: '1.25', note: '$15/yr · Save 37%' },
  au:  { m: '6.99', a: '4.99', note: '$59.99/yr · Save 28%' }
};
function toggleBilling() {
  annual = !annual;
  const toggle = document.getElementById('billToggle');
  toggle.classList.toggle('on', annual);
  document.getElementById('lbl-mo').classList.toggle('on', !annual);
  document.getElementById('lbl-yr').classList.toggle('on', annual);
  ['us','ca','uk','au'].forEach(c => {
    const amountEl = document.querySelector(`.p-amount[data-mo="${priceData[c].m}"]`);
    const noteEl = document.getElementById('note-' + c);
    if (amountEl) {
      amountEl.style.transform = 'translateY(-6px)';
      amountEl.style.opacity = '0';
      setTimeout(() => {
        amountEl.textContent = annual ? priceData[c].a : priceData[c].m;
        amountEl.style.transform = 'translateY(0)';
        amountEl.style.opacity = '1';
        amountEl.style.transition = 'transform .3s cubic-bezier(.34,1.56,.64,1),opacity .3s';
      }, 150);
    }
    if (noteEl) noteEl.textContent = annual ? priceData[c].note : '';
  });
}

/* ─── FAQ ─── */
function toggleFaq(el) {
  const item = el.closest('.faq-item');
  const wasOpen = item.classList.contains('open');
  document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
  if (!wasOpen) item.classList.add('open');
}

/* ─── DIALER ─── */
let dialInput = '';
function dPress(key) {
  if (key === '⌫') { dialInput = dialInput.slice(0, -1); }
  else if (dialInput.length < 14) { dialInput += key; }
  const numEl = document.getElementById('d-num');
  numEl.textContent = dialInput || '+1 (555)';
  // Flash feedback
  numEl.style.color = 'var(--sky)';
  setTimeout(() => numEl.style.color = '#fff', 180);
}
function dCall(btn) {
  btn.style.background = 'linear-gradient(135deg,var(--coral),#ff8b8e)';
  btn.style.boxShadow = '0 6px 24px rgba(255,94,98,.5)';
  setTimeout(() => {
    btn.style.background = 'var(--grad-teal)';
    btn.style.boxShadow = '0 6px 20px rgba(6,199,160,.4)';
  }, 2200);
}

/* ─── Hero background: mouse + scroll parallax (background-position, keeps CSS zoom) ─── */
const heroGridBg = document.querySelector('.hero-grid-bg');
let heroBgScrollY = 0;
function applyHeroBgParallax(mouseX = 0, mouseY = 0) {
  if (!heroGridBg || window.innerWidth < 768) return;
  const yShift = Math.min(heroBgScrollY * 0.04, 24);
  const xPos = 78 + mouseX * 0.4;
  const yPos = 48 + yShift + mouseY * 0.35;
  heroGridBg.style.backgroundPosition = `${xPos}% ${yPos}%, 0 0, 0 0`;
}
document.addEventListener('mousemove', (e) => {
  const x = (e.clientX / window.innerWidth - 0.5) * 16;
  const y = (e.clientY / window.innerHeight - 0.5) * 10;
  applyHeroBgParallax(x, y);
});
window.addEventListener('scroll', () => {
  heroBgScrollY = window.scrollY;
  applyHeroBgParallax();
  const bannerImg = document.querySelector('.feat-banner-img');
  const banner = document.querySelector('.feat-image-banner');
  if (bannerImg && banner) {
    const rect = banner.getBoundingClientRect();
    if (rect.top < window.innerHeight && rect.bottom > 0) {
      const p = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / (window.innerHeight + rect.height * 0.5)));
      bannerImg.style.transform = `scale(${1.02 + p * 0.05}) translateY(${p * -14}px)`;
    }
  }
}, { passive: true });

/* ─── MOUSE TRACKING for image hover effects ─── */
document.querySelectorAll('.feat-image-banner, .trust-img-ph').forEach(el => {
  el.addEventListener('mousemove', (e) => {
    const rect = el.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    el.style.setProperty('--mouse-x', `${x}%`);
    el.style.setProperty('--mouse-y', `${y}%`);
  });
});

/* ─── IMAGE PARALLAX ON SCROLL ─── */
const parallaxImages = document.querySelectorAll('.trust-img, .feat-banner-img, .p-flag-img');
const parallaxObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('parallax-active');
    } else {
      entry.target.classList.remove('parallax-active');
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

parallaxImages.forEach(img => {
  parallaxObserver.observe(img);
});

window.addEventListener('scroll', () => {
  parallaxImages.forEach(img => {
    if (!img.classList.contains('parallax-active')) return;
    const rect = img.getBoundingClientRect();
    const scrollProgress = Math.max(0, Math.min(1, (window.innerHeight - rect.top) / window.innerHeight));
    const translateY = (scrollProgress - 0.5) * 20;
    img.style.transform = `translateY(${translateY}px) scale(${1 + scrollProgress * 0.05})`;
  });
}, { passive: true });

/* HD strip: stagger setup steps on reveal */
const hdObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (!entry.isIntersecting) return;
    entry.target.querySelectorAll('.setup-step').forEach((step, i) => {
      step.style.transition = `opacity .5s ease ${i * 0.1}s, transform .5s cubic-bezier(.16,1,.3,1) ${i * 0.1}s, box-shadow .3s, border-color .25s`;
      step.style.opacity = '1';
      step.style.transform = 'translateY(0)';
    });
    hdObserver.unobserve(entry.target);
  });
}, { threshold: 0.2 });
const hdStrip = document.querySelector('.feat-hd-full');
if (hdStrip) {
  hdStrip.querySelectorAll('.setup-step').forEach(step => {
    step.style.opacity = '0';
    step.style.transform = 'translateY(12px)';
  });
  hdObserver.observe(hdStrip);
}

/* ─── NUM CARD CLICK EFFECT ─── */
document.querySelectorAll('.num-card').forEach(card => {
  card.addEventListener('click', function() {
    document.querySelectorAll('.num-card').forEach(c => {
      c.classList.remove('active');
      c.querySelector('.live-ring')?.classList.remove('live-ring');
    });
    this.classList.add('active');
    // Add click ripple animation
    const ripple = document.createElement('div');
    ripple.style.cssText = 'position:absolute;inset:0;border-radius:inherit;background:rgba(6,199,160,.2);animation:cardRipple .5s ease forwards;pointer-events:none';
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 500);
  });
});

/* Add card ripple animation keyframes */
const style = document.createElement('style');
style.textContent = `@keyframes cardRipple{from{opacity:1;transform:scale(0.8)}to{opacity:0;transform:scale(1.5)}}`;
document.head.appendChild(style);

/* ─── SMOOTH SCROLL for anchor links ─── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

/* ─── MAGNETIC BUTTON EFFECT ─── */
document.querySelectorAll('.btn-hero-primary, .btn-cta-nav, .btn-p-solid, .btn-vip').forEach(btn => {
  btn.addEventListener('mousemove', (e) => {
    const rect = btn.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    btn.style.transform = `translate(${x * 0.15}px, ${y * 0.15}px) scale(1.02)`;
  });
  btn.addEventListener('mouseleave', () => {
    btn.style.transform = '';
  });
});

/* ─── IMAGE LAZY REVEAL ANIMATION ─── */
const imageRevealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0) scale(1)';
      imageRevealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.trust-img, .feat-banner-img, .p-flag-img').forEach(img => {
  img.style.opacity = '0';
  img.style.transform = 'translateY(30px) scale(0.95)';
  img.style.transition = 'opacity 0.8s ease, transform 0.8s cubic-bezier(0.16,1,0.3,1)';
  imageRevealObserver.observe(img);
});