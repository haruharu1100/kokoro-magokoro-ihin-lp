# 心まごころ遺品整理 LP

GitHub Pagesで無料公開できる静的LPです。

## 公開前に差し替える値

`index.html` の `window.LP_CONFIG` を編集してください。

- `phoneNumber`: 実際の電話番号
- `lineUrl`: LINE公式アカウントのURL
- `ga4MeasurementId`: GA4の測定ID
- `googleAdsId`: Google広告タグID
- `googleAdsConversionLabel`: Google広告コンバージョンラベル

Search Consoleを使う場合は、`meta name="google-site-verification"` の `content` も差し替えます。

## GitHub Pages公開手順

1. GitHubで新規リポジトリを作成
2. このフォルダの中身をリポジトリ直下へアップロード
3. GitHubの `Settings` → `Pages`
4. `Build and deployment` を `Deploy from a branch`
5. Branchを `main`、Folderを `/root` にして保存
6. 数分後に `https://ユーザー名.github.io/リポジトリ名/` で公開

## 広告運用メモ

- 電話クリック、LINEクリック、無料見積もりボタンは `gtag` イベントを送信します。
- Google広告IDとコンバージョンラベルを入れると、電話・LINE・無料見積もりボタンをコンバージョンとして送信します。
- `utm_source`、`utm_medium`、`utm_campaign`、`utm_term`、`gclid` はhidden項目へ保存されます。

## 公式LINE AI返信

`api/line-webhook.js` にLINE Messaging API用のWebhookを用意しています。
GitHub Pagesではサーバー機能が動かないため、AI返信はVercelなどに公開して使います。

必要な環境変数:

```env
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
```

Webhook URL:

```text
https://公開URL/api/line-webhook
```

ローカル確認:

```bash
npm run check
```
