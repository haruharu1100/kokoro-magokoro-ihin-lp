(() => {
if (window.__kokoroLpScriptLoaded) return;
window.__kokoroLpScriptLoaded = true;

const config = window.LP_CONFIG || {};
const lineOfficialId = "@357phpan";
const roomSelect = document.querySelector("#roomSelect");
const volumeSelect = document.querySelector("#volumeSelect");
const estimate = document.querySelector("#estimate");
const form = document.querySelector("#contactForm");
const formNote = document.querySelector("#formNote");

const placeholderValues = new Set([
  "G-XXXXXXXXXX",
  "AW-XXXXXXXXXX",
  "YOUR_CONVERSION_LABEL",
  "https://line.me/R/ti/p/@YOUR_LINE_ID",
  "0120-000-000"
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
        span.textContent = `${config.phoneNumber} / 9:00〜18:00`;
      }
    });
  }

  if (hasRealValue(config.lineUrl)) {
    document.querySelectorAll(".js-line-link").forEach((link) => {
      link.href = config.lineUrl;
    });
  }

  if (form && hasRealValue(config.lineUrl)) {
    form.action = config.lineUrl;
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

function normalizedPhoneNumber() {
  const phone = hasRealValue(config.phoneNumber) ? config.phoneNumber : "0745-51-1665";
  return {
    display: phone,
    href: `tel:${phone.replace(/[^\d+]/g, "")}`
  };
}

function fieldValue(name) {
  const field = form?.elements?.[name];
  return field ? field.value.trim() : "";
}

function buildLineMessage() {
  if (!form) return "";
  const lines = [
    "無料見積もりをお願いします。",
    "",
    `お名前: ${fieldValue("name") || "未入力"}`,
    `電話番号: ${fieldValue("tel") || "未入力"}`,
    `エリア: ${fieldValue("area") || "未入力"}`,
    `相談内容: ${fieldValue("type") || "未入力"}`,
    `詳細: ${fieldValue("message") || "未入力"}`,
    "",
    "間取り、物量、希望日、立ち会い可否が分かれば追って送ります。"
  ];
  return lines.join("\n");
}

function lineMessageUrl() {
  const message = buildLineMessage();
  const hasInput = ["name", "tel", "area", "message"].some((name) => fieldValue(name));
  if (!hasInput) return config.lineUrl;
  return `https://line.me/R/oaMessage/${encodeURIComponent(lineOfficialId)}/?${encodeURIComponent(message)}`;
}

function updateLineSubmitHref() {
  document.querySelectorAll('[data-track="line_form_submit"]').forEach((link) => {
    link.href = lineMessageUrl();
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

document.querySelectorAll(".js-phone-link").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    const phone = normalizedPhoneNumber();
    const confirmed = window.confirm(`${phone.display}に電話しますか？`);

    if (!confirmed) return;

    const label = link.dataset.track || "phone_confirmed";
    trackEvent("phone_confirmed", { event_category: "lead", event_label: label });
    trackAdsConversion(label);
    window.location.href = phone.href;
  });
});

document.querySelectorAll("[data-track]").forEach((element) => {
  element.addEventListener("click", (event) => {
    if (element.classList.contains("js-phone-link")) return;
    const label = element.dataset.track;
    trackEvent("lp_click", { event_category: "engagement", event_label: label });
    if (label === "line_form_submit" || label === "line_contact" || label === "line_hero" || label === "line_sticky") {
      trackEvent(label, { event_category: "lead", event_label: label });
    }
    if (label && (label.startsWith("phone") || label.startsWith("line"))) {
      trackAdsConversion(label);
    }
    if (label === "line_form_submit") {
      event.preventDefault();
      window.location.href = lineMessageUrl();
    }
  });
});

form?.addEventListener("submit", (event) => {
  event.preventDefault();
  trackEvent("generate_lead", { event_category: "lead", event_label: "form_submit" });
  trackAdsConversion("form_submit");

  if (hasRealValue(config.lineUrl)) {
    window.location.href = lineMessageUrl();
    return;
  }

  if (formNote) {
    formNote.textContent = "公式LINEのURLが未設定です。LINE公式アカウントのURLを設定してください。";
    formNote.style.color = "#c94f45";
  }
});

roomSelect?.addEventListener("change", updateEstimate);
volumeSelect?.addEventListener("change", updateEstimate);
["name", "tel", "area", "type", "message"].forEach((name) => {
  form?.elements?.[name]?.addEventListener("input", updateLineSubmitHref);
  form?.elements?.[name]?.addEventListener("change", updateLineSubmitHref);
});

applyRuntimeConfig();
loadTracking();
captureCampaignParams();
updateLineSubmitHref();
})();
