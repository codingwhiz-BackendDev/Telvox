// Mobile sidebar toggle
const mobileToggle = document.getElementById('mobileToggle');
const sidebar = document.getElementById('sidebar');

if (mobileToggle && sidebar) {
  mobileToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
  if (window.innerWidth <= 768) {
    if (!sidebar.contains(e.target) && !mobileToggle.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  }
});

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
      alert(`You have selected ${selectedNumber}. In production, this would process the payment and activate the number.`);
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
    
    if (!amount || amount <= 0) {
      alert('Please enter a valid amount');
      return;
    }
    
    if (termsCheckbox && !termsCheckbox.checked) {
      alert('Please agree to the Terms & Conditions');
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
      alert('Please fill in all card details');
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
    alert('Payment confirmed! In production, this would process the payment.');
    window.location.href = '/webdialer/account/';
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
