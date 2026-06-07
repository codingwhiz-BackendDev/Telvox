// Notification system
function showNotification(type, title, message, duration = 5000) {
  const container = document.getElementById('notificationContainer');
  if (!container) {
    console.error('Notification container not found');
    return;
  }
  
  // Ensure container has proper positioning
  container.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    left: auto;
    bottom: auto;
    z-index: 9999999;
    display: flex;
    flex-direction: column;
    gap: 12px;
    pointer-events: none;
    max-height: calc(100vh - 40px);
    overflow-y: auto;
    width: auto;
    max-width: 400px;
  `;
  
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  
  // Add inline styles to ensure visibility
  notification.style.cssText = `
    min-width: 300px;
    max-width: 400px;
    padding: 16px 20px;
    border-radius: 12px;
    background: #151a2d;
    border: 1px solid rgba(255, 255, 255, 0.1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    display: flex;
    align-items: center;
    gap: 12px;
    position: relative;
    overflow: hidden;
    color: #ffffff;
    margin-bottom: 0;
    z-index: 9999999;
    pointer-events: auto;
    width: 100%;
    box-sizing: border-box;
  `;
  
  const icons = {
    success: '<svg width="24" height="24" fill="none" stroke="#10b981" stroke-width="2" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>',
    error: '<svg width="24" height="24" fill="none" stroke="#ef4444" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>',
    warning: '<svg width="24" height="24" fill="none" stroke="#f59e0b" stroke-width="2" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',
    info: '<svg width="24" height="24" fill="none" stroke="#3b82f6" stroke-width="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>'
  };
  
  notification.innerHTML = `
    <div class="notification-icon" style="width: 24px; height: 24px; flex-shrink: 0;">${icons[type] || icons.info}</div>
    <div class="notification-content" style="flex: 1;">
      <div class="notification-title" style="font-weight: 600; font-size: 0.95rem; color: #ffffff; margin-bottom: 4px;">${title}</div>
      <div class="notification-message" style="font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); line-height: 1.4;">${message}</div>
    </div>
    <button class="notification-close" style="width: 24px; height: 24px; background: transparent; border: none; color: rgba(255, 255, 255, 0.7); cursor: pointer; display: flex; align-items: center; justify-content: center; border-radius: 6px; flex-shrink: 0;">
      <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
    </button>
  `;
  
  container.appendChild(notification);
  
  // Add color strip based on type
  const colors = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6'
  };
  
  const colorStrip = document.createElement('div');
  colorStrip.style.cssText = `
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: ${colors[type] || colors.info};
  `;
  notification.appendChild(colorStrip);
  
  // Close button functionality
  const closeBtn = notification.querySelector('.notification-close');
  closeBtn.addEventListener('click', () => {
    notification.style.opacity = '0';
    notification.style.transform = 'translateX(100%)';
    notification.style.transition = 'all 0.3s ease-out';
    setTimeout(() => notification.remove(), 300);
  });
  
  // Auto dismiss
  if (duration > 0) {
    setTimeout(() => {
      if (notification.parentNode) {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'all 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
      }
    }, duration);
  }
}

// Mobile sidebar toggle
const mobileToggle = document.getElementById('mobileToggle');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

if (mobileToggle && sidebar && sidebarOverlay) {
  mobileToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    sidebarOverlay.classList.toggle('active');
  });

  // Close sidebar when clicking overlay
  sidebarOverlay.addEventListener('click', () => {
    sidebar.classList.remove('open');
    sidebarOverlay.classList.remove('active');
  });

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target) && !sidebarOverlay.contains(e.target)) {
        sidebar.classList.remove('open');
        sidebarOverlay.classList.remove('active');
      }
    }
  });
}

// Account tabs
const tabBtns = document.querySelectorAll('.tab-btn');
const tabPanes = document.querySelectorAll('.tab-pane');

tabBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    const tabName = btn.dataset.tab;
    
    tabBtns.forEach(b => b.classList.remove('active'));
    tabPanes.forEach(p => p.classList.remove('active'));
    
    btn.classList.add('active');
    const activePane = document.getElementById(tabName);
    if (activePane) {
      activePane.classList.add('active');
    }
  });
});

// FAQ accordion
const faqQuestions = document.querySelectorAll('.faq-question');

faqQuestions.forEach(question => {
  question.addEventListener('click', () => {
    const faqItem = question.parentElement;
    faqItem.classList.toggle('active');
  });
});

// Top-up cards selection
const topupCards = document.querySelectorAll('.topup-card');
const customAmountInput = document.getElementById('customAmount');

topupCards.forEach(card => {
  card.addEventListener('click', () => {
    topupCards.forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    
    if (customAmountInput) {
      customAmountInput.value = card.dataset.amount;
    }
  });
});

// Conversation selection in SMS
const conversationItems = document.querySelectorAll('.conversation-item');

conversationItems.forEach(item => {
  item.addEventListener('click', () => {
    const conversationId = item.dataset.conversationId;
    window.location.href = `?conversation=${conversationId}`;
  });
});

// Duration format filter (can be used in templates)
function formatDuration(seconds) {
  if (seconds < 60) {
    return `${seconds}s`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
}

// Phone dialer functionality
const dialerInput = document.getElementById('dialerInput');
const dialerCallBtn = document.getElementById('dialerCallBtn');
const dialerBackspace = document.getElementById('dialerBackspace');
const dialerStatus = document.getElementById('dialerStatus');
const dialerKeys = document.querySelectorAll('.dialer-key');

if (dialerInput) {
  // Handle keypad button clicks
  dialerKeys.forEach(key => {
    key.addEventListener('click', () => {
      const value = key.dataset.value;
      dialerInput.value += value;
    });
  });
  
  // Handle backspace
  if (dialerBackspace) {
    dialerBackspace.addEventListener('click', () => {
      dialerInput.value = dialerInput.value.slice(0, -1);
    });
  }
  
  // Handle call button
  if (dialerCallBtn) {
    dialerCallBtn.addEventListener('click', () => {
      const phoneNumber = dialerInput.value.trim();
      
      if (!phoneNumber) {
        if (dialerStatus) {
          dialerStatus.textContent = 'Please enter a phone number';
          dialerStatus.className = 'dialer-status error';
        }
        return;
      }
      
      // Check if user has credits (balance > 0)
      const balanceElement = document.querySelector('.dialer-balance-amount');
      const balance = balanceElement ? parseFloat(balanceElement.textContent.replace('$', '')) : 0;
      
      if (balance <= 0) {
        if (dialerStatus) {
          dialerStatus.textContent = 'Insufficient balance. Please top up your account.';
          dialerStatus.className = 'dialer-status error';
        }
        return;
      }
      
      // Simulate call initiation
      if (dialerStatus) {
        dialerStatus.textContent = `Calling ${phoneNumber}...`;
        dialerStatus.className = 'dialer-status success';
      }
      
      dialerCallBtn.disabled = true;
      
      // Simulate call connection (in production, this would make an actual API call)
      setTimeout(() => {
        if (dialerStatus) {
          dialerStatus.textContent = 'Call initiated successfully';
          dialerStatus.className = 'dialer-status success';
        }
        dialerInput.value = '';
        dialerCallBtn.disabled = false;
        
        // Clear status after 3 seconds
        setTimeout(() => {
          if (dialerStatus) {
            dialerStatus.textContent = '';
          }
        }, 3000);
      }, 1500);
    });
  }
}

// Payment flow functionality
const continueToPayment = document.getElementById('continueToPayment');
const backToRecharge = document.getElementById('backToRecharge');
const proceedToPay = document.getElementById('proceedToPay');
const backToVerify = document.getElementById('backToVerify');
const confirmPayment = document.getElementById('confirmPayment');
const rechargeAmount = document.getElementById('rechargeAmount');
const packageCards = document.querySelectorAll('.package-card');
const termsCheckbox = document.getElementById('termsCheckbox');

// Dialer toggle functionality
const dialerToggle = document.getElementById('dialerToggle');
const phoneDialer = document.querySelector('.phone-dialer');
const mainContent = document.querySelector('.main-content');
const mainContentInner = document.querySelector('.main-content-inner');

if (dialerToggle && phoneDialer) {
  dialerToggle.addEventListener('click', () => {
    phoneDialer.classList.toggle('hidden');
    mainContent.classList.toggle('dialer-hidden');
    mainContentInner.classList.toggle('dialer-hidden');
    dialerToggle.classList.toggle('active');
  });
}

// Message search functionality
const messageSearch = document.getElementById('messageSearch');

if (messageSearch && conversationItems.length > 0) {
  messageSearch.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    
    conversationItems.forEach(item => {
      const phoneNumber = item.querySelector('.conv-number').textContent.toLowerCase();
      const preview = item.querySelector('.conv-preview').textContent.toLowerCase();
      
      if (phoneNumber.includes(searchTerm) || preview.includes(searchTerm)) {
        item.style.display = '';
      } else {
        item.style.display = 'none';
      }
    });
  });
}

// Get number modal functionality
const openGetNumberModal = document.getElementById('openGetNumberModal');
const openGetNumberModalFromEmpty = document.getElementById('openGetNumberModalFromEmpty');
const getNumberModal = document.getElementById('getNumberModal');
const closeGetNumberModal = document.getElementById('closeGetNumberModal');
const countrySelect = document.getElementById('countrySelect');
const availableNumbers = document.getElementById('availableNumbers');
const selectedNumberSummary = document.getElementById('selectedNumberSummary');
const selectedNumberDisplay = document.getElementById('selectedNumberDisplay');
const confirmGetNumber = document.getElementById('confirmGetNumber');
const selectNumberButtons = document.querySelectorAll('.btn-select-number');
const numberOptions = document.querySelectorAll('.number-option');

let selectedNumber = null;

// Open modal
if (openGetNumberModal) {
  openGetNumberModal.addEventListener('click', () => {
    getNumberModal.classList.add('active');
  });
}

if (openGetNumberModalFromEmpty) {
  openGetNumberModalFromEmpty.addEventListener('click', () => {
    getNumberModal.classList.add('active');
  });
}

// Close modal
if (closeGetNumberModal) {
  closeGetNumberModal.addEventListener('click', () => {
    getNumberModal.classList.remove('active');
    resetGetNumberForm();
  });
}

// Close modal on outside click
if (getNumberModal) {
  getNumberModal.addEventListener('click', (e) => {
    if (e.target === getNumberModal) {
      getNumberModal.classList.remove('active');
      resetGetNumberForm();
    }
  });
}

// Select number
selectNumberButtons.forEach((btn, index) => {
  btn.addEventListener('click', () => {
    numberOptions.forEach(opt => opt.classList.remove('selected'));
    numberOptions[index].classList.add('selected');
    selectedNumber = numberOptions[index].querySelector('.number-display').textContent;
    selectedNumberDisplay.textContent = selectedNumber;
    selectedNumberSummary.style.display = 'block';
    confirmGetNumber.disabled = false;
  });
});

// Confirm get number
if (confirmGetNumber) {
  confirmGetNumber.addEventListener('click', () => {
    if (selectedNumber) {
      showNotification('info', 'Number Selected', `You have selected ${selectedNumber}. In production, this would process the payment and activate the number.`);
      getNumberModal.classList.remove('active');
      resetGetNumberForm();
    }
  });
}

// Reset form
function resetGetNumberForm() {
  selectedNumber = null;
  if (countrySelect) {
    countrySelect.value = '';
  }
  numberOptions.forEach(opt => opt.classList.remove('selected'));
  selectedNumberSummary.style.display = 'none';
  if (confirmGetNumber) {
    confirmGetNumber.disabled = true;
  }
}

let selectedAmount = 0;
let selectedBonus = 0;

// Package selection
packageCards.forEach(card => {
  card.addEventListener('click', () => {
    packageCards.forEach(c => c.classList.remove('selected'));
    card.classList.add('selected');
    selectedAmount = parseFloat(card.dataset.amount);
    selectedBonus = parseFloat(card.dataset.bonus);
    if (rechargeAmount) {
      rechargeAmount.value = selectedAmount;
    }
  });
});

// Continue to payment details
if (continueToPayment) {
  continueToPayment.addEventListener('click', () => {
    const amount = rechargeAmount ? parseFloat(rechargeAmount.value) : selectedAmount;
    
    if (!amount || amount < 5) {
      showNotification('error', 'Invalid Amount', 'Minimum amount is $5. Please enter a valid amount to proceed.');
      return;
    }
    
    if (termsCheckbox && !termsCheckbox.checked) {
      showNotification('warning', 'Terms Required', 'Please agree to the Terms & Conditions to continue.');
      return;
    }
    
    selectedAmount = amount;
    updatePaymentSummary();
    goToStep(2);
  });
}

// Back to recharge
if (backToRecharge) {
  backToRecharge.addEventListener('click', () => {
    goToStep(1);
  });
}

// Proceed to pay
if (proceedToPay) {
  proceedToPay.addEventListener('click', () => {
    const cardNumber = document.querySelector('.card-number-input');
    const cardExpiry = document.querySelector('.card-expiry-input');
    const cardCvv = document.querySelector('.card-cvv-input');
    const cardName = document.querySelector('.card-name-input');
    
    if (!cardNumber.value || !cardExpiry.value || !cardCvv.value || !cardName.value) {
      showNotification('error', 'Missing Information', 'Please fill in all card details to proceed.');
      return;
    }
    
    updatePaymentConfirmation();
    goToStep(3);
  });
}

// Back to verify
if (backToVerify) {
  backToVerify.addEventListener('click', () => {
    goToStep(2);
  });
}

// Confirm payment
if (confirmPayment) {
  confirmPayment.addEventListener('click', () => {
    showNotification('success', 'Payment Confirmed', 'Payment confirmed! In production, this would process the payment.');
    setTimeout(() => {
      window.location.href = '/webdialer/account/';
    }, 1500);
  });
}

// Go to specific step
function goToStep(stepNumber) {
  const progressSteps = document.querySelectorAll('.progress-step');
  const stepContents = document.querySelectorAll('.payment-step-content');
  
  progressSteps.forEach((step, index) => {
    if (index + 1 <= stepNumber) {
      step.classList.add('active');
    } else {
      step.classList.remove('active');
    }
  });
  
  stepContents.forEach(content => {
    const contentStep = parseInt(content.dataset.step);
    if (contentStep === stepNumber) {
      content.classList.add('active');
    } else {
      content.classList.remove('active');
    }
  });
}

// Update payment summary
function updatePaymentSummary() {
  const summaryAmount = document.getElementById('summaryAmount');
  const summaryBonus = document.getElementById('summaryBonus');
  const summaryTotal = document.getElementById('summaryTotal');
  
  if (summaryAmount) {
    summaryAmount.textContent = `$${selectedAmount.toFixed(2)}`;
  }
  if (summaryBonus) {
    summaryBonus.textContent = `+$${selectedBonus.toFixed(2)}`;
  }
  if (summaryTotal) {
    summaryTotal.textContent = `$${(selectedAmount + selectedBonus).toFixed(2)}`;
  }
}

// Update payment confirmation
function updatePaymentConfirmation() {
  const finalAmount = document.getElementById('finalAmount');
  const finalCredits = document.getElementById('finalCredits');
  
  if (finalAmount) {
    finalAmount.textContent = `$${selectedAmount.toFixed(2)}`;
  }
  if (finalCredits) {
    finalCredits.textContent = `$${(selectedAmount + selectedBonus).toFixed(2)}`;
  }
}
