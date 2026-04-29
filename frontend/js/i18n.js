// ===========================
// i18n (English / Hindi / Gujarati)
// ===========================

const SUPPORTED_LANGS = ['en', 'hi', 'gu'];
const DEFAULT_LANG = 'en';

// Minimal key-based translations for UI strings.
// Keep keys stable; values can evolve without touching logic.
const TRANSLATIONS = {
  en: {
    app_title: 'Farm Monitor',
    app_subtitle: 'Satellite Health & Weather Analysis',
    language_label: 'Language',

    how_to_use_title: 'How to Use',
    how_to_use_1: 'Zoom to your farm location on the map',
    how_to_use_2: 'Click the polygon tool (⬟) to draw your field',
    how_to_use_3: 'Click points to create the field boundary',
    how_to_use_4: 'Enter farm details and click "Generate Report"',

    farm_details_title: 'Farm Details',
    farm_name_label: 'Farm Name *',
    farm_name_placeholder: 'e.g., Green Valley Farm',
    crop_type_label: 'Crop Type *',
    crop_select_placeholder: 'Select crop...',
    email_label: 'Email (optional)',
    email_placeholder: 'your@email.com',
    email_help: 'Receive report via email',
    email_delivery_note: 'We try our best to deliver emails, but delivery is not guaranteed.',
    planting_date_label: 'Planting Date (optional)',
    planting_date_help: 'Helps determine crop growth stage',

    generate_report: 'Generate Report',
    processing: 'Processing...',
    clear_field: 'Clear Field',
    find_my_location: 'Find My Location',

    loading_title: 'Analyzing Your Farm...',
    loading_status_connecting_satellite: 'Connecting to satellite...',
    loading_status_connecting_server: 'Connecting to server...',
    loading_status_processing: 'Processing your request...',
    step1: 'Fetching satellite data',
    step2: 'Retrieving weather data',
    step3: 'Calculating NDVI',
    step4: 'Generating PDF report',

    result_title: 'Report Ready!',
    download_pdf: 'Download PDF Report',
    new_report: 'Create New Report',

    error_title: 'Error',
    try_again: 'Try Again',

    field_area_label: 'Field Area:',
    coordinates_label: 'Coordinates:',

    report_summary_title: 'Report Summary',
    report_farm: 'Farm:',
    report_crop: 'Crop:',
    report_area: 'Area:',
    report_ndvi: 'NDVI:',
    report_health: 'Health Status:',
    report_recommendations: 'Recommendations:',

    pdf_filename_suffix: 'report',

    map_you_are_here: 'You are here!',
    geo_not_supported: 'Geolocation is not supported by your browser',
    geo_unavailable_prefix: 'Unable to get your location: ',

    err_draw_field_polygon: 'Please draw a field polygon on the map',
    err_enter_farm_name: 'Please enter a farm name',
    err_select_crop: 'Please select a crop type',
    err_valid_email: 'Please enter a valid email address',
    err_draw_field_first: 'Please draw a field on the map first',
    err_download_pdf: 'Failed to download PDF',
    err_request_validation_failed: 'Request validation failed. Please check your inputs.',
    err_unexpected: 'An unexpected error occurred. Please try again.',
    err_backend_sleeping:
      'Unable to connect to the server. The free tier may be sleeping. Please wait 30-60 seconds and try again.'
    ,
    backend_wake_note:
      'Note: Our free backend may take 30–60 seconds to wake up after inactivity. If it fails, please try again after 60 seconds.'
  },

  hi: {
    app_title: 'फार्म मॉनिटर',
    app_subtitle: 'उपग्रह स्वास्थ्य और मौसम विश्लेषण',
    language_label: 'भाषा',

    how_to_use_title: 'कैसे उपयोग करें',
    how_to_use_1: 'मानचित्र पर अपने खेत के स्थान तक ज़ूम करें',
    how_to_use_2: 'अपने खेत की सीमा बनाने के लिए बहुभुज टूल (⬟) पर क्लिक करें',
    how_to_use_3: 'सीमा बनाने के लिए बिंदुओं पर क्लिक करें',
    how_to_use_4: 'खेत का विवरण भरें और "रिपोर्ट बनाएँ" पर क्लिक करें',

    farm_details_title: 'खेत का विवरण',
    farm_name_label: 'खेत का नाम *',
    farm_name_placeholder: 'जैसे, ग्रीन वैली फार्म',
    crop_type_label: 'फसल का प्रकार *',
    crop_select_placeholder: 'फसल चुनें...',
    email_label: 'ईमेल (वैकल्पिक)',
    email_placeholder: 'your@email.com',
    email_help: 'ईमेल पर रिपोर्ट प्राप्त करें',
    email_delivery_note: 'हम ईमेल भेजने की पूरी कोशिश करते हैं, लेकिन डिलीवरी की गारंटी नहीं है।',
    planting_date_label: 'रोपाई/बुआई की तारीख (वैकल्पिक)',
    planting_date_help: 'फसल की वृद्धि अवस्था निर्धारित करने में मदद करता है',

    generate_report: 'रिपोर्ट बनाएँ',
    processing: 'प्रोसेस हो रहा है...',
    clear_field: 'खेत साफ़ करें',
    find_my_location: 'मेरा स्थान ढूँढें',

    loading_title: 'आपके खेत का विश्लेषण हो रहा है...',
    loading_status_connecting_satellite: 'उपग्रह से कनेक्ट हो रहा है...',
    loading_status_connecting_server: 'सर्वर से कनेक्ट हो रहा है...',
    loading_status_processing: 'आपका अनुरोध प्रोसेस हो रहा है...',
    step1: 'उपग्रह डेटा प्राप्त हो रहा है',
    step2: 'मौसम डेटा प्राप्त हो रहा है',
    step3: 'NDVI की गणना हो रही है',
    step4: 'PDF रिपोर्ट बन रही है',

    result_title: 'रिपोर्ट तैयार है!',
    download_pdf: 'PDF रिपोर्ट डाउनलोड करें',
    new_report: 'नई रिपोर्ट बनाएँ',

    error_title: 'त्रुटि',
    try_again: 'फिर से कोशिश करें',

    field_area_label: 'खेत का क्षेत्रफल:',
    coordinates_label: 'निर्देशांक:',

    report_summary_title: 'रिपोर्ट सारांश',
    report_farm: 'खेत:',
    report_crop: 'फसल:',
    report_area: 'क्षेत्रफल:',
    report_ndvi: 'NDVI:',
    report_health: 'स्वास्थ्य स्थिति:',
    report_recommendations: 'सिफ़ारिशें:',

    pdf_filename_suffix: 'रिपोर्ट',

    map_you_are_here: 'आप यहाँ हैं!',
    geo_not_supported: 'आपके ब्राउज़र में जियोलोकेशन समर्थित नहीं है',
    geo_unavailable_prefix: 'आपका स्थान प्राप्त नहीं हो सका: ',

    err_draw_field_polygon: 'कृपया मानचित्र पर खेत का बहुभुज बनाइए',
    err_enter_farm_name: 'कृपया खेत का नाम दर्ज करें',
    err_select_crop: 'कृपया फसल का प्रकार चुनें',
    err_valid_email: 'कृपया एक मान्य ईमेल दर्ज करें',
    err_draw_field_first: 'कृपया पहले मानचित्र पर खेत बनाइए',
    err_download_pdf: 'PDF डाउनलोड करने में विफल',
    err_request_validation_failed: 'अनुरोध सत्यापन विफल। कृपया इनपुट जाँचें।',
    err_unexpected: 'कोई अप्रत्याशित त्रुटि हुई। कृपया फिर से कोशिश करें।',
    err_backend_sleeping:
      'सर्वर से कनेक्ट नहीं हो पा रहा। फ्री टियर स्लीप में हो सकता है। 30-60 सेकंड प्रतीक्षा करके फिर कोशिश करें।'
    ,
    backend_wake_note:
      'नोट: हमारा फ्री बैकएंड निष्क्रियता के बाद 30–60 सेकंड में जागता है। यदि विफल हो, तो 60 सेकंड बाद फिर प्रयास करें।'
  },

  gu: {
    app_title: 'ફાર્મ મોનિટર',
    app_subtitle: 'ઉપગ્રહ આરોગ્ય અને હવામાન વિશ્લેષણ',
    language_label: 'ભાષા',

    how_to_use_title: 'કેવી રીતે ઉપયોગ કરવો',
    how_to_use_1: 'નકશા પર તમારા ખેતરના સ્થાન પર ઝૂમ કરો',
    how_to_use_2: 'ખેતરની સીમા દોરવા માટે બહુકોણ ટૂલ (⬟) પર ક્લિક કરો',
    how_to_use_3: 'સીમા બનાવવા માટે બિંદુઓ પર ક્લિક કરો',
    how_to_use_4: 'ખેતરની વિગતો ભરો અને "રિપોર્ટ બનાવો" પર ક્લિક કરો',

    farm_details_title: 'ખેતરની વિગતો',
    farm_name_label: 'ખેતરનું નામ *',
    farm_name_placeholder: 'જેમ કે, ગ્રીન વેલી ફાર્મ',
    crop_type_label: 'પાકનો પ્રકાર *',
    crop_select_placeholder: 'પાક પસંદ કરો...',
    email_label: 'ઇમેઇલ (વૈકલ્પિક)',
    email_placeholder: 'your@email.com',
    email_help: 'ઇમેઇલ પર રિપોર્ટ મેળવો',
    email_delivery_note: 'અમે ઇમેઇલ મોકલવાનો સંપૂર્ણ પ્રયાસ કરીએ છીએ, પરંતુ ડિલિવરીની ખાતરી નથી.',
    planting_date_label: 'વાવણીની તારીખ (વૈકલ્પિક)',
    planting_date_help: 'પાકની વૃદ્ધિ સ્થિતિ જાણવા મદદ કરે છે',

    generate_report: 'રિપોર્ટ બનાવો',
    processing: 'પ્રક્રિયા ચાલુ છે...',
    clear_field: 'ખેતર સાફ કરો',
    find_my_location: 'મારું સ્થાન શોધો',

    loading_title: 'તમારા ખેતરનું વિશ્લેષણ થઈ રહ્યું છે...',
    loading_status_connecting_satellite: 'ઉપગ્રહ સાથે જોડાઈ રહ્યું છે...',
    loading_status_connecting_server: 'સર્વર સાથે જોડાઈ રહ્યું છે...',
    loading_status_processing: 'તમારી વિનંતી પ્રક્રિયા થઈ રહી છે...',
    step1: 'ઉપગ્રહ ડેટા મેળવી રહ્યું છે',
    step2: 'હવામાન ડેટા મેળવી રહ્યું છે',
    step3: 'NDVI ગણતરી થઈ રહી છે',
    step4: 'PDF રિપોર્ટ બની રહ્યો છે',

    result_title: 'રિપોર્ટ તૈયાર છે!',
    download_pdf: 'PDF રિપોર્ટ ડાઉનલોડ કરો',
    new_report: 'નવી રિપોર્ટ બનાવો',

    error_title: 'ભૂલ',
    try_again: 'ફરી પ્રયાસ કરો',

    field_area_label: 'ખેતરનું ક્ષેત્રફળ:',
    coordinates_label: 'સંયોજક:',

    report_summary_title: 'રિપોર્ટ સારાંશ',
    report_farm: 'ખેતર:',
    report_crop: 'પાક:',
    report_area: 'ક્ષેત્રફળ:',
    report_ndvi: 'NDVI:',
    report_health: 'આરોગ્ય સ્થિતિ:',
    report_recommendations: 'ભલામણો:',

    pdf_filename_suffix: 'રિપોર્ટ',

    map_you_are_here: 'તમે અહીં છો!',
    geo_not_supported: 'તમારા બ્રાઉઝરમાં જિયોલોકેશન સપોર્ટેડ નથી',
    geo_unavailable_prefix: 'તમારું સ્થાન મેળવી શક્યા નથી: ',

    err_draw_field_polygon: 'કૃપા કરીને નકશા પર ખેતરનો બહુકોણ દોરો',
    err_enter_farm_name: 'કૃપા કરીને ખેતરનું નામ દાખલ કરો',
    err_select_crop: 'કૃપા કરીને પાકનો પ્રકાર પસંદ કરો',
    err_valid_email: 'કૃપા કરીને માન્ય ઇમેઇલ દાખલ કરો',
    err_draw_field_first: 'કૃપા કરીને પહેલા નકશા પર ખેતર દોરો',
    err_download_pdf: 'PDF ડાઉનલોડ કરવામાં નિષ્ફળ',
    err_request_validation_failed: 'વિનંતી ચકાસણી નિષ્ફળ. કૃપા કરીને ઇનપુટ તપાસો.',
    err_unexpected: 'અણધારી ભૂલ થઈ. કૃપા કરીને ફરી પ્રયાસ કરો.',
    err_backend_sleeping:
      'સર્વર સાથે જોડાઈ શકાતું નથી. ફ્રી ટિયર સૂઈ ગયું હોઈ શકે. 30-60 સેકંડ રાહ જોઈને ફરી પ્રયાસ કરો.'
    ,
    backend_wake_note:
      'નોંધ: અમારો ફ્રી બેકએન્ડ નિષ્ક્રિયતા બાદ 30–60 સેકંડમાં જાગે છે. જો નિષ્ફળ જાય તો 60 સેકંડ પછી ફરી પ્રયાસ કરો.'
  }
};

function normalizeLang(lang) {
  if (typeof lang !== 'string') return DEFAULT_LANG;
  const lower = lang.toLowerCase();
  if (SUPPORTED_LANGS.includes(lower)) return lower;
  return DEFAULT_LANG;
}

function getStoredLang() {
  try {
    const v = window.localStorage.getItem('fm_lang');
    return normalizeLang(v || DEFAULT_LANG);
  } catch {
    return DEFAULT_LANG;
  }
}

function setStoredLang(lang) {
  const normalized = normalizeLang(lang);
  try {
    window.localStorage.setItem('fm_lang', normalized);
  } catch {
    // ignore
  }
  return normalized;
}

function t(key) {
  const lang = window.I18N.getLanguage();
  const table = TRANSLATIONS[lang] || TRANSLATIONS[DEFAULT_LANG];
  return table[key] || (TRANSLATIONS[DEFAULT_LANG] && TRANSLATIONS[DEFAULT_LANG][key]) || key;
}

function applyTranslations() {
  const lang = window.I18N.getLanguage();

  // html lang attribute helps screenreaders.
  document.documentElement.setAttribute('lang', lang);

  // Text nodes
  document.querySelectorAll('[data-i18n]').forEach((el) => {
    const key = el.getAttribute('data-i18n');
    if (!key) return;
    el.textContent = t(key);
  });

  // Placeholders
  document.querySelectorAll('[data-i18n-placeholder]').forEach((el) => {
    const key = el.getAttribute('data-i18n-placeholder');
    if (!key) return;
    el.setAttribute('placeholder', t(key));
  });
}

function initLanguageSelector(selectEl) {
  if (!selectEl) return;

  // Populate options
  const current = window.I18N.getLanguage();
  selectEl.innerHTML = '';
  const opts = [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'हिन्दी' },
    { value: 'gu', label: 'ગુજરાતી' }
  ];
  opts.forEach((o) => {
    const opt = document.createElement('option');
    opt.value = o.value;
    opt.textContent = o.label;
    if (o.value === current) opt.selected = true;
    selectEl.appendChild(opt);
  });

  selectEl.addEventListener('change', () => {
    window.I18N.setLanguage(selectEl.value);
  });
}

// Expose a small API to the rest of the app.
window.I18N = {
  t,
  getLanguage() {
    return getStoredLang();
  },
  setLanguage(lang) {
    const normalized = setStoredLang(lang);
    applyTranslations();
    const selectEl = document.getElementById('languageSelect');
    if (selectEl && selectEl.value !== normalized) selectEl.value = normalized;
    return normalized;
  },
  init() {
    // Ensure a sane value is stored, then translate.
    setStoredLang(getStoredLang());
    applyTranslations();
    initLanguageSelector(document.getElementById('languageSelect'));
  },
  SUPPORTED_LANGS
};

