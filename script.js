const config = window.LP_CONFIG || {};
const roomSelect = document.querySelector("#roomSelect");
const volumeSelect = document.querySelector("#volumeSelect");
const estimate = document.querySelector("#estimate");
const form = document.querySelector("#contactForm");
const formNote = document.querySelector("#formNote");

const placeholderValues = new Set([
  "G-XXXXXXXXXX",
  "AW-XXXXXXXXXX",
  "YOUR_CONVERSION_LABEL",
  "https://formspree.io/f/YOUR_FORM_ID",
  "https://line.me/R/ti/p/@YOUR_LINE_ID",
  "0120-000-000",
  "info@example.com"
]);

function hasRealValue(value) {
  return Boolean(value) && !placeholderValues.has(value);
}

function formatYen(value) {
  return `${(Math.round(value / 1000) * 1000).toLocaleString("ja-JP")}円〜`;
}

function updateEstimate() {
  if (!roomSelect || !volumeSelect || !estimate) return;
  const base = Number(roomSelect.value);
  const volume = Number(volumeSelect.value);
  estimate.textContent = formatYen(base * volume);
}

function applyRuntimeConfig() {
  if (hasRealValue(config.phoneNumber)) {
    document.querySelectorAll(".js-phone-link").forEach((link) => {
      link.href = `tel:${config.phoneNumber.replace(/[^\d+]/g, "")}`;
      if (link.classList.contains("tel")) link.textContent = config.phoneNumber;
      const span = link.querySelector("span");
      if (span && span.textContent.includes("0120-000-000")) {
        span.textContent = `${config.phoneNumber} / 8:00〜22:00`;
      }
    });
  }

  if (hasRealValue(config.mailAddress)) {
    document.querySelectorAll(".js-mail-link").forEach((link) => {
      link.href = `mailto:${config.mailAddress}`;
      const span = link.querySelector("span");
      if (span) span.textContent = config.mailAddress;
    });
  }

  if (hasRealValue(config.lineUrl)) {
    document.querySelectorAll(".js-line-link").forEach((link) => {
      link.href = config.lineUrl;
    });
  }

  if (form && hasRealValue(config.formEndpoint)) {
    form.action = config.formEndpoint;
  }
}

function loadTracking() {
  const ids = [config.ga4MeasurementId, config.googleAdsId].filter(hasRealValue);
  if (!ids.length) return;

  window.dataLayer = window.dataLayer || [];
  window.gtag = function gtag(){ window.dataLayer.push(arguments); };
  window.gtag("js", new Date());
  ids.forEach((id) => window.gtag("config", id));

  const script = document.createElement("script");
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${ids[0]}`;
  document.head.appendChild(script);
}

function trackEvent(name, params = {}) {
  if (typeof window.gtag === "function") {
    window.gtag("event", name, params);
  }
}

function trackAdsConversion(eventName) {
  if (!hasRealValue(config.googleAdsId) || !hasRealValue(config.googleAdsConversionLabel)) return;
  trackEvent("conversion", {
    send_to: `${config.googleAdsId}/${config.googleAdsConversionLabel}`,
    event_category: "lead",
    event_label: eventName
  });
}

function captureCampaignParams() {
  const params = new URLSearchParams(window.location.search);
  const keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "gclid"];
  keys.forEach((key) => {
    const value = params.get(key) || localStorage.getItem(key) || "";
    if (params.get(key)) localStorage.setItem(key, params.get(key));
    const field = document.querySelector(`#${key.replace(/_([a-z])/g, (_, c) => c.toUpperCase())}`);
    if (field) field.value = value;
  });
  const pageUrl = document.querySelector("#pageUrl");
  if (pageUrl) pageUrl.value = window.location.href;
}

document.querySelectorAll("[data-track]").forEach((element) => {
  element.addEventListener("click", () => {
    const label = element.dataset.track;
    trackEvent("lp_click", { event_category: "engagement", event_label: label });
    if (label && (label.startsWith("phone") || label.startsWith("line"))) {
      trackAdsConversion(label);
    }
  });
});

form?.addEventListener("submit", (event) => {
  trackEvent("generate_lead", { event_category: "lead", event_label: "form_submit" });
  trackAdsConversion("form_submit");

  if (!hasRealValue(form.action) || form.action.includes("YOUR_FORM_ID")) {
    event.preventDefault();
    if (formNote) {
      formNote.textContent = "フォーム送信先が未設定です。Formspreeなどの送信先URLを入れると、そのまま受信できます。";
      formNote.style.color = "#c94f45";
    }
  }
});

roomSelect?.addEventListener("change", updateEstimate);
volumeSelect?.addEventListener("change", updateEstimate);

applyRuntimeConfig();
loadTracking();
captureCampaignParams();
