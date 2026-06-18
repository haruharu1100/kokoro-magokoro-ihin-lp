const webhook = require("../api/line-webhook");

const sample = [
  "作業場所の市区町村　奈良",
  "2. 間取り　4ldk",
  "3. 物量　多い",
  "4. 希望時期　4/15",
  "5. 立ち会いの可否　なし",
  "6. 写真があれば数枚　6枚"
].join("\n");

console.log(webhook._test.fallbackReply(sample));

console.log("\n--- contact only ---\n");
console.log(webhook._test.fallbackReply("田中\n電話08014558894"));
