const crypto = require("crypto");

const LINE_REPLY_ENDPOINT = "https://api.line.me/v2/bot/message/reply";
const OPENAI_RESPONSES_ENDPOINT = "https://api.openai.com/v1/responses";

const BUSINESS_CONTEXT = `
あなたは「心まごころ遺品整理」の公式LINE一次対応AIです。

基本情報:
- 公式LINE ID: @357phpan
- 対応エリア: 大阪、兵庫、奈良、京都
- 営業時間: 9:00〜18:00
- 電話番号: 0745-51-1665
- 主なサービス: 遺品整理 / 生前整理 / 供養 / 買取

役割:
- 最初のあいさつ
- LPから届いた名前、電話番号、エリア、相談内容、詳細の確認
- 不足情報の聞き返し
- 写真送付の案内
- 担当者が返信する旨の案内
- クレームやトラブル時の一次受け

守ること:
- 丁寧で落ち着いた日本語にする。
- 長すぎず、LINEで読みやすい文量にする。
- 金額確定、日程確定、作業可否の断定はしない。
- クレーム、トラブル、急ぎ、特殊清掃、孤独死、強い臭気、害虫、体液、血液、法的・相続問題は担当者に引き継ぐ。
- ユーザーが十分な情報を送っている場合は「担当者が確認して返信します」と案内する。
- 間取り、物量、希望時期、立ち会い可否、写真が不足している場合は、分かる範囲で追加依頼する。
- 営業時間外でも受付はできるが、返信は営業時間内になる場合があると案内する。
`;

function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}

function verifyLineSignature(rawBody, signature, channelSecret) {
  if (!signature || !channelSecret) return false;
  const digest = crypto
    .createHmac("sha256", channelSecret)
    .update(rawBody)
    .digest("base64");
  const expected = Buffer.from(digest);
  const actual = Buffer.from(signature);
  return expected.length === actual.length && crypto.timingSafeEqual(expected, actual);
}

function hasEnoughLeadInfo(text) {
  const estimateDetails = [
    /作業場所|市区町村|エリア|住所|市|区|町|村|大阪|兵庫|奈良|京都/.test(text),
    /間取り|1K|1DK|1LDK|2DK|2LDK|3DK|3LDK|4DK|4LDK|5LDK|ldk|LDK|dk|DK/.test(text),
    /物量|多い|少ない|普通|荷物|家具|家電/.test(text),
    /希望時期|希望日|今日|明日|今月|来月|\d{1,2}\/\d{1,2}|\d{1,2}月/.test(text),
    /立ち会い|立会|あり|なし|可能|不可/.test(text),
    /写真|枚|画像/.test(text)
  ];
  if (estimateDetails.filter(Boolean).length >= 3) return true;

  const checks = [
    /お名前|名前|氏名/.test(text),
    /電話番号|TEL|tel|携帯|090|080|070/.test(text),
    /エリア|住所|市|区|町|村|大阪|兵庫|奈良|京都/.test(text),
    /相談内容|遺品整理|生前整理|供養|買取/.test(text),
    /詳細|間取り|物量|希望|立ち会い|写真/.test(text)
  ];
  return checks.filter(Boolean).length >= 4;
}

function hasContactInfo(text) {
  const hasName = /お名前|名前|氏名|田中|山田|様/.test(text);
  const hasPhone = /電話番号|電話|TEL|tel|携帯|090|080|070|0\d{1,4}[-\s]?\d{1,4}[-\s]?\d{3,4}/.test(text);
  return hasName || hasPhone;
}

function isComplaintOrEscalation(text) {
  return /クレーム|苦情|怒|返金|キャンセル|トラブル|ひどい|最悪|連絡がない|孤独死|特殊清掃|臭|害虫|血液|体液|相続|法律/.test(text);
}

function fallbackReply(userText) {
  if (isComplaintOrEscalation(userText)) {
    return [
      "ご不安な思いをさせてしまい申し訳ございません。",
      "内容を正確に確認し、担当者より直接ご連絡いたします。",
      "",
      "恐れ入りますが、お名前・お電話番号・状況の詳細をお送りください。"
    ].join("\n");
  }

  if (hasEnoughLeadInfo(userText)) {
    return [
      "ありがとうございます。",
      "ご入力内容を確認しました。",
      "",
      "担当者が内容を確認して返信いたしますので、少々お待ちください。",
      "お部屋全体や荷物量が分かる写真があれば、続けて送っていただくと概算見積もりがスムーズです。",
      "",
      "お名前とお電話番号がまだの場合は、あわせてお送りください。"
    ].join("\n");
  }

  if (hasContactInfo(userText)) {
    return [
      "ありがとうございます。",
      "お名前・お電話番号を確認しました。",
      "",
      "概算見積もりのため、分かる範囲で下記も教えてください。",
      "",
      "1. 作業場所の市区町村",
      "2. 間取り",
      "3. 物量",
      "4. 希望時期",
      "5. 立ち会いの可否",
      "6. 写真があれば数枚",
      "",
      "分かる範囲だけで大丈夫です。"
    ].join("\n");
  }

  return [
    "お問い合わせありがとうございます。",
    "心まごころ遺品整理です。",
    "",
    "概算見積もりのため、分かる範囲で下記を教えてください。",
    "",
    "1. 作業場所の市区町村",
    "2. 間取り",
    "3. 物量",
    "4. 希望時期",
    "5. 立ち会いの可否",
    "6. 写真があれば数枚",
    "",
    "急ぎの場合はお電話でも対応できます。",
    "0745-51-1665"
  ].join("\n");
}

async function createAiReply(userText) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return fallbackReply(userText);

  const response = await fetch(OPENAI_RESPONSES_ENDPOINT, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${apiKey}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      model: process.env.OPENAI_MODEL || "gpt-4.1-mini",
      input: [
        {
          role: "system",
          content: BUSINESS_CONTEXT
        },
        {
          role: "user",
          content: `お客様からのLINEメッセージ:\n${userText}\n\nこの内容に返信してください。`
        }
      ],
      max_output_tokens: 420
    })
  });

  if (!response.ok) {
    console.error("OpenAI API error", response.status, await response.text());
    return fallbackReply(userText);
  }

  const data = await response.json();
  const text = data.output_text || "";
  return text.trim() || fallbackReply(userText);
}

async function replyToLine(replyToken, text) {
  const token = process.env.LINE_CHANNEL_ACCESS_TOKEN;
  if (!token) throw new Error("LINE_CHANNEL_ACCESS_TOKEN is missing");

  const response = await fetch(LINE_REPLY_ENDPOINT, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      replyToken,
      messages: [
        {
          type: "text",
          text: text.slice(0, 4900)
        }
      ]
    })
  });

  if (!response.ok) {
    throw new Error(`LINE reply failed: ${response.status} ${await response.text()}`);
  }
}

module.exports = async function handler(req, res) {
  if (req.method === "GET") {
    res.status(200).json({
      ok: true,
      service: "kokoro-magokoro-line-ai",
      webhook: "/api/line-webhook"
    });
    return;
  }

  if (req.method !== "POST") {
    res.setHeader("Allow", "GET, POST");
    res.status(405).json({ ok: false, error: "Method not allowed" });
    return;
  }

  const rawBody = await readRawBody(req);
  const signature = req.headers["x-line-signature"];
  const channelSecret = process.env.LINE_CHANNEL_SECRET;

  if (!verifyLineSignature(rawBody, signature, channelSecret)) {
    res.status(401).json({ ok: false, error: "Invalid LINE signature" });
    return;
  }

  let payload;
  try {
    payload = JSON.parse(rawBody);
  } catch (error) {
    res.status(400).json({ ok: false, error: "Invalid JSON" });
    return;
  }

  try {
    const events = Array.isArray(payload.events) ? payload.events : [];
    await Promise.all(events.map(async (event) => {
      if (event.type !== "message" || event.message?.type !== "text" || !event.replyToken) {
        return;
      }

      const userText = event.message.text || "";
      const reply = await createAiReply(userText);
      await replyToLine(event.replyToken, reply);
    }));

    res.status(200).json({ ok: true });
  } catch (error) {
    console.error(error);
    res.status(500).json({ ok: false, error: "Webhook handling failed" });
  }
};

module.exports._test = {
  fallbackReply,
  hasEnoughLeadInfo,
  isComplaintOrEscalation
};
