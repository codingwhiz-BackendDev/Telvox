/* ─── RIPPLE ─── */
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

document.querySelectorAll('.has-ripple').forEach(btn => {
  btn.addEventListener('click', e => addRipple(e, btn));
});

/* ─── MAP PARALLAX (mouse) ─── */
const mapImg = document.querySelector('.auth-map-img');
const mapWrap = document.querySelector('.auth-map-wrap');
const authVisual = document.querySelector('.auth-visual');

document.addEventListener('mousemove', e => {
  if (!mapImg || window.innerWidth < 960) return;
  const x = (e.clientX / window.innerWidth - 0.5) * 20;
  const y = (e.clientY / window.innerHeight - 0.5) * 14;
  mapImg.style.transform = `scale(1.03) translate(${x * 0.35}px, ${y * 0.3}px)`;
});

/* ─── MOUSE TRACKING for button hover effects ─── */
document.querySelectorAll('.btn-google').forEach(btn => {
  btn.addEventListener('mousemove', (e) => {
    const rect = btn.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    btn.style.setProperty('--mouse-x', `${x}%`);
    btn.style.setProperty('--mouse-y', `${y}%`);
  });
});

/* ─── FLOATING ELEMENTS INTERACTION ─── */
document.querySelectorAll('.auth-float').forEach(float => {
  float.addEventListener('mouseenter', () => {
    float.style.animationPlayState = 'paused';
  });
  float.addEventListener('mouseleave', () => {
    float.style.animationPlayState = 'running';
  });
});

/* ─── PULSE POINTS INTERACTION ─── */
document.querySelectorAll('.auth-pulse').forEach(pulse => {
  pulse.addEventListener('click', () => {
    pulse.style.transform = 'scale(1.5)';
    pulse.style.transition = 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1)';
    setTimeout(() => {
      pulse.style.transform = 'scale(1)';
    }, 300);
  });
});

/* ─── GOOGLE LINK: brief loading state before navigation ─── */
const btnGoogle = document.getElementById('btnGoogle');
if (btnGoogle && btnGoogle.tagName === 'A') {
  btnGoogle.addEventListener('click', function () {
    const label = this.querySelector('.btn-google-text');
    const icon = this.querySelector('.btn-google-icon');
    if (label && icon) {
      this.classList.add('loading');
      label.textContent = 'Redirecting to Google…';
      icon.innerHTML = '<span class="btn-google-spinner"></span>';
    }
  });
}

/* ─── STAGGER ENTRANCE for card children ─── */
document.querySelectorAll('.auth-card-head, .btn-google, .auth-foot, .auth-trust, .auth-legal').forEach((el, i) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(12px)';
  el.style.transition = `opacity .6s cubic-bezier(.16,1,.3,1) ${0.35 + i * 0.08}s, transform .6s cubic-bezier(.16,1,.3,1) ${0.35 + i * 0.08}s`;
  requestAnimationFrame(() => {
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, 50);
  });
});

/* ─── AUTH CARD HOVER EFFECT ─── */
const authCard = document.querySelector('.auth-card');
if (authCard) {
  authCard.addEventListener('mousemove', (e) => {
    const rect = authCard.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    authCard.style.transform = `translateY(-4px) rotateX(${y * 2}deg) rotateY(${x * 2}deg)`;
  });
  authCard.addEventListener('mouseleave', () => {
    authCard.style.transform = 'translateY(0)';
  });
}

/* ─── LOGO HOVER ANIMATION ─── */
const authLogo = document.querySelector('.auth-logo');
if (authLogo) {
  authLogo.addEventListener('mouseenter', () => {
    const logoMark = authLogo.querySelector('.auth-logo-mark');
    if (logoMark) {
      logoMark.style.transform = 'rotate(-6deg) scale(1.1)';
    }
  });
  authLogo.addEventListener('mouseleave', () => {
    const logoMark = authLogo.querySelector('.auth-logo-mark');
    if (logoMark) {
      logoMark.style.transform = '';
    }
  });
}

/* ─── SMOOTH TRANSITION between auth pages ─── */
window.addEventListener('beforeunload', () => {
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.3s ease';
});

/* ─── INPUT FOCUS EFFECTS (if inputs are added later) ─── */
const addInputFocusEffects = () => {
  document.querySelectorAll('input').forEach(input => {
    input.addEventListener('focus', () => {
      input.parentElement.style.transform = 'translateY(-2px)';
    });
    input.addEventListener('blur', () => {
      input.parentElement.style.transform = '';
    });
  });
};

// Call when DOM is ready
document.addEventListener('DOMContentLoaded', addInputFocusEffects);
