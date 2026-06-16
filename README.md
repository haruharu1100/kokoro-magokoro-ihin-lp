# 心まごころ遺品整理 LP

GitHub Pagesで無料公開できる静的LPです。

## 公開前に差し替える値

`index.html` の `window.LP_CONFIG` を編集してください。

- `phoneNumber`: 実際の電話番号
- `mailAddress`: 問い合わせ用メール
- `lineUrl`: LINE公式アカウントのURL
- `formEndpoint`: Formspreeなどのフォーム送信先URL
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

- 電話クリック、LINEクリック、フォーム送信は `gtag` イベントを送信します。
- Google広告IDとコンバージョンラベルを入れると、電話・LINE・フォームをコンバージョンとして送信します。
- `utm_source`、`utm_medium`、`utm_campaign`、`utm_term`、`gclid` はフォームのhidden項目へ保存されます。
