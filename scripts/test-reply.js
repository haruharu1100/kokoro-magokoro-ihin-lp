const webhook = require("../api/line-webhook");

const sample = [
  "作業場所の市区町村　奈良",
  "2. 間取り　4ldk",
  "3. 物量　多い",
  "4. 希望時期　4/15",
  "5. 立ち会いの可否　なし",
  "6. 写真があれば数枚　6枚"
].join("\n");

console.log(webhook._test.templateReply(sample));

console.log("\n--- contact only ---\n");
console.log(webhook._test.templateReply("田中\n電話08014558894"));

console.log("\n--- full after contact ---\n");
console.log(webhook._test.templateReply([
  "遺品整理の見積もりお願いします。",
  "奈良県です。",
  "4LDKで物量は多いです。",
  "希望日は4/15です。",
  "立ち会いなし希望です。",
  "写真は6枚送れます。",
  "名前田中",
  "電話08014558848"
].join("\n")));
