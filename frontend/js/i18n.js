/**
 * MahaSeva AI - Comprehensive Multilingual Engine
 * Handles en (English), mr (Marathi), and hi (Hindi)
 */

const MahaI18n = {
  currentLanguage: 'mr',
  dictionaries: {},
  terminology: {},
  dynamicCache: {},

  async init() {
    // 1. Check localStorage for persistent language
    const savedLang = localStorage.getItem('mahaSeva_language');
    if (savedLang && ['en', 'mr', 'hi'].includes(savedLang)) {
      this.currentLanguage = savedLang;
    } else {
      // 2. Detect browser language
      const browserLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
      if (browserLang.startsWith('mr')) {
        this.currentLanguage = 'mr';
      } else if (browserLang.startsWith('hi')) {
        this.currentLanguage = 'hi';
      } else {
        this.currentLanguage = 'en';
      }
      localStorage.setItem('mahaSeva_language', this.currentLanguage);
    }

    // 3. Load dictionaries
    await this.loadDictionaries();

    // 4. Update document metadata
    this.updateDocumentAttributes();
  },

  async loadDictionaries() {
    try {
      const [enRes, mrRes, hiRes, termRes] = await Promise.all([
        fetch('/i18n/en.json'),
        fetch('/i18n/mr.json'),
        fetch('/i18n/hi.json'),
        fetch('/i18n/terminology/government_terms.json')
      ]);

      if (enRes.ok) this.dictionaries.en = await enRes.json();
      if (mrRes.ok) this.dictionaries.mr = await mrRes.json();
      if (hiRes.ok) this.dictionaries.hi = await hiRes.json();
      if (termRes.ok) this.terminology = await termRes.json();
    } catch (e) {
      console.warn('Fallback: Using embedded translations dictionary');
    }
  },

  setLanguage(lang) {
    if (!['en', 'mr', 'hi'].includes(lang)) return;
    this.currentLanguage = lang;
    localStorage.setItem('mahaSeva_language', lang);
    this.updateDocumentAttributes();

    // Trigger reactive UI re-render across the entire app
    if (typeof window.renderCurrentView === 'function') {
      window.renderCurrentView();
    }
  },

  updateDocumentAttributes() {
    document.documentElement.lang = this.currentLanguage;
    document.documentElement.dir = 'ltr';

    const titles = {
      en: 'MahaSeva AI | Maharashtra Government Services',
      mr: 'महासेवा AI | महाराष्ट्र शासन नागरिक सेवा गेटवे',
      hi: 'महासेवा AI | महाराष्ट्र सरकारी सेवाएं'
    };
    document.title = titles[this.currentLanguage] || titles.mr;

    // Update active button classes in navbar
    ['en', 'mr', 'hi'].forEach(l => {
      const btn = document.getElementById(`lang-${l}`);
      if (btn) {
        if (l === this.currentLanguage) {
          btn.className = "px-2.5 py-1 rounded font-bold bg-amber-500 text-slate-950 shadow transition";
          btn.setAttribute('aria-pressed', 'true');
        } else {
          btn.className = "px-2.5 py-1 rounded text-slate-300 hover:text-white font-medium transition";
          btn.setAttribute('aria-pressed', 'false');
        }
      }
    });
  },

  t(key, params = {}) {
    const dict = this.dictionaries[this.currentLanguage] || this.dictionaries.en || {};
    let text = dict[key];

    if (!text && this.dictionaries.en) {
      text = this.dictionaries.en[key]; // fallback to english
    }

    if (!text) {
      return key; // return key if translation missing
    }

    // Replace parameter placeholders e.g. {days}, {count}
    Object.keys(params).forEach(p => {
      text = text.replace(new RegExp(`\\{${p}\\}`, 'g'), params[p]);
    });

    return text;
  },

  formatNumber(num) {
    if (num === null || num === undefined || isNaN(num)) return '';
    try {
      const locale = this.currentLanguage === 'mr' ? 'mr-IN' : (this.currentLanguage === 'hi' ? 'hi-IN' : 'en-IN');
      return new Intl.NumberFormat(locale).format(num);
    } catch (e) {
      return num.toLocaleString();
    }
  },

  formatCurrency(amount) {
    if (amount === null || amount === undefined || isNaN(amount)) return '₹0';
    try {
      const locale = this.currentLanguage === 'mr' ? 'mr-IN' : (this.currentLanguage === 'hi' ? 'hi-IN' : 'en-IN');
      return new Intl.NumberFormat(locale, { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount);
    } catch (e) {
      return `₹${amount.toLocaleString()}`;
    }
  },

  formatDate(dateStr) {
    if (!dateStr) return '';
    try {
      const locale = this.currentLanguage === 'mr' ? 'mr-IN' : (this.currentLanguage === 'hi' ? 'hi-IN' : 'en-IN');
      const d = new Date(dateStr);
      return new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(d);
    } catch (e) {
      return dateStr;
    }
  },

  async translateDynamic(text, sourceLang = 'en') {
    if (!text || sourceLang === this.currentLanguage) return text;
    const cacheKey = `${sourceLang}:${this.currentLanguage}:${text}`;
    if (this.dynamicCache[cacheKey]) {
      return this.dynamicCache[cacheKey];
    }

    try {
      const res = await fetch('/api/v1/translation/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          source_language: sourceLang,
          target_language: this.currentLanguage
        })
      });
      if (res.ok) {
        const data = await res.json();
        this.dynamicCache[cacheKey] = data.translated_text;
        return data.translated_text;
      }
    } catch (e) {
      // return original text on failure
    }
    return text;
  }
};

// Global helper function for shorthand t('key')
function t(key, params = {}) {
  return MahaI18n.t(key, params);
}

function setLanguage(lang) {
  MahaI18n.setLanguage(lang);
}
