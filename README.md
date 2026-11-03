# shikumi-zukuri.com

「しくみづくり」の Web サイト（1 枚ものの LP）。

https://shikumi-zukuri.com/

## 構成

| パス | 内容 |
| --- | --- |
| `public/` | 公開するファイル（HTML / CSS / favicon）。ビルド不要 |
| `tools/gen_contours.py` | ヒーローの等高線 SVG パスを生成するスクリプト（作り直すときだけ使う） |
| `wrangler.jsonc` | Cloudflare Workers（静的アセット）の設定 |
| `.github/workflows/deploy.yml` | master への push で Cloudflare にデプロイする CI |

## ローカルで確認

```bash
cd public
python3 -m http.server 8787
# http://127.0.0.1:8787/ を開く
```

## デプロイ

`master` に push すると GitHub Actions が `wrangler deploy` を実行する。

事前に GitHub リポジトリの Secrets に以下を登録しておくこと。

- `CLOUDFLARE_API_TOKEN`: 「Edit Cloudflare Workers」テンプレートで作成した API トークン
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare のアカウント ID
