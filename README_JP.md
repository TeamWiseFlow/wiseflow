# AI チーフインテリジェンスオフィサー（Wiseflow）

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **インターネット全体から必要な情報を継続的に抽出します**

主要な自メディアプラットフォーム、事前ログインが必要なサイト、特定の情報源の追跡、スケジュールタスクによる毎日の収集、大規模言語モデルによる自動抽出（要約モード、カスタムフォームモード）などをサポートしています……

## 🎉 WiseFlow Pro バージョンがリリースされました！

より強力なクローリング機能、より包括的なソーシャルメディアサポート、Web UI 搭載、およびワンクリックインストールパッケージ！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥🔥 **Pro バージョンは現在全世界で発売中**：https://shouxiqingbaoguan.com/ 

🌹 本日より、wiseflow オープンソースバージョンへの PR（コード、ドキュメント、成功事例の共有を歓迎）を提供し、採用された貢献者には wiseflow pro バージョンの 1 年間使用権を贈呈します！

## Wiseflow オープンソース版

バージョン 4.30 以降、wiseflow オープンソース版は pro 版と同じアーキテクチャにアップグレードされ、同じ API を備えており、[wiseflow+](https://github.com/TeamWiseFlow/wiseflow-plus) エコシステムをシームレスに共有できます！

🎁 限定オファー：住宅用プロキシの無料試用と 2,000 回の無料 SERP API 呼び出しにサインアップ！

<a href="https://www.thordata.com/products/serp-api?ls=github&lk=wiseflow" target="_blank"><img src="./docs/logos/thordata_en.png" alt="Thordata" height="120"/></a>

## wiseflow オープンソースバージョンと pro バージョンの比較

| 機能特性 | オープンソース版 | Pro 版 |
| :--- | :---: | :---: |
| **監視対象信源** | web、rss | web、rss、さらに 7 つの主要な中国自媒体プラットフォーム |
| **検索ソース** | bing、github、arxiv | bing、github、arxiv、さらに 6 つの主要な中国自媒体プラットフォーム |
| **インストール** | 手動で環境構築とデプロイが必要 | インストール不要、ワンクリック実行 |
| **ユーザーインターフェース** | なし | 中国語 web UI |
| **LLM 費用** | ユーザー自身で LLM サービスを購読またはローカル LLM を構築 | サブスクリプションに LLM 呼び出し費用が含まれる (追加設定不要) |
| **技術サポート** | GitHub Issues | 有料ユーザー向け WeChat グループ |
| **価格** | 無料 | ￥488/年 |
| **適用グループ** | コミュニティ探索とプロジェクト学習 | 日常的な使用（個人または企業） |

## 🧐 wiseflow の製品ポジショニング

wiseflow は ChatGPT や Manus のような汎用的なエージェントではありません。情報監視と抽出に特化しており、ユーザーが指定したソースをサポートし、定期的なタスクモードで常に最新情報を取得することを保証します（1 日最大 4 回、つまり 6 時間ごとの取得をサポート）。また、wiseflow は指定されたプラットフォームからの包括的な情報検索（例えば「人探し」）をサポートします。

しかし、wiseflow を従来の意味でのクローラーや RPA と同一視しないでください！ wiseflow の取得動作は完全に LLM によって駆動され、ヘッドレスブラウザや仮想ブラウザではなく本物のブラウザを使用して行われ、取得と抽出の動作が同時に実行されます：

- 革新的な HTML インテリジェント解析メカニズム：重要な情報とさらに探索可能なリンクを自動的に識別します。
- 「クローリングと検索の一体化」戦略：クローリングプロセス中に LLM がリアルタイムで判断と抽出を行い、関連情報のみをキャプチャすることで、リスクコントロールのリスクを大幅に低減します。
- 真にすぐに使用可能：Xpath、スクリプト、または手動設定は不要で、一般ユーザーでも簡単に使用できます。

    ……

詳細は以下をご参照ください：https://shouxiqingbaoguan.com/

## 🌟 クイックスタート

**たった 3 ステップで開始できます！**

**4.2 バージョン以降、Google Chrome ブラウザのインストールが必須です（デフォルトのインストールパスを使用）。**

**Windows ユーザーは事前に Git Bash ツールをダウンロードし、bash で以下のコマンドを実行してください。[bash ダウンロードリンク](https://git-scm.com/downloads/win)**

### 📋 環境管理ツール uv のインストールと wiseflow ソースコードのダウンロード

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

上記の操作で uv のインストールが完了し、wiseflow のソースコードがダウンロードされます。

### 📥 env_sample を参考に .env ファイルを設定

wiseflow フォルダ（プロジェクトルートディレクトリ）で env_sample を参考に .env ファイルを作成し、関連する設定情報（主に llm サービスの設定）を入力してください。

**wiseflow オープンソースバージョンはユーザー自身で llm サービスを設定する必要があります。**

wiseflow はモデルサービスプロバイダーを限定しません。OpenAI SDK のリクエストインターフェース形式と互換性があれば、既存の Maas サービスや Ollama などのローカルデプロイモデルサービスを選択できます。

中国大陸のユーザーには、Siliconflow モデルサービスの使用をお勧めします。

😄 私の [推奨リンク](https://cloud.siliconflow.cn/i/WNLYbBpi) を使用して申請していただけると、私たち両方とも ￥14 のプラットフォーム報酬を獲得できます。

OpenAI などの海外のクローズドソースモデルを使用したい場合は、中国大陸でスムーズに動作する AiHubMix モデルサービスを使用できます：

😄 私の [AiHubMix 招待リンク](https://aihubmix.com?aff=Gp54) を使用して登録してください。

海外のユーザーは、Siliconflow の国際版を使用できます：https://www.siliconflow.com/

### 🚀 起動！

```bash
cd wiseflow
uv venv # 初回実行時のみ必要
source .venv/bin/activate  # Linux/macOS
# または Windows 上：
# .venv\Scripts\activate
uv sync # 初回実行時のみ必要
python core/entry.py
```

## 📚 自作プログラムで wiseflow が取得したデータを使用する方法

[wiseflow backend api](./core/backend/README.md) を参照してください。

wiseflow ベースであろうと wiseflow-pro ベースであろうと、以下のリポジトリであなたの活用事例を共有し、宣伝していただくことを歓迎します！

- https://github.com/TeamWiseFlow/wiseflow-plus

（このリポジトリへの PR 貢献も、採用された場合は wiseflow-pro の 1 年間使用権が贈呈されます）

**4.2x バージョンのアーキテクチャは 4.30 と完全な互換性はありません。4.2x の最終バージョン（v4.29）はメンテナンスが終了しています。コードの参照が必要な場合は、"2025" ブランチに切り替えてください。**

## 🛡️ ライセンス

4.2 バージョン以降、オープンソースライセンスを更新しました。詳細はこちらをご確認ください： [LICENSE](LICENSE) 

商用協力については、**Email：zm.zhao@foxmail.com** までご連絡ください。

## 📬 連絡先

ご質問やご提案がありましたら、[issue](https://github.com/TeamWiseFlow/wiseflow/issues) を通じてメッセージを残してください。

pro バージョンに関する要望や協力のフィードバックについては、AI チーフインテリジェンスオフィサー「掌柜」の企業用 WeChat までご連絡ください：

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 本プロジェクトは以下の優れたオープンソースプロジェクトに基づいています：

- Crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- Patchright (Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihu crawler） https://github.com/NanmiCoder/MediaCrawler
- NoDriver（ウェブ自動化、ウェブスクレイピング、ボット、その他の創造的なアイデアのための高速フレームワークを提供） https://github.com/ultrafunkamsterdam/nodriver
- Feedparser（Python でフィードを解析） https://github.com/kurtmckee/feedparser
- SearXNG（様々な検索サービスやデータベースからの結果を集約するフリーのインターネットメタ検索エンジン） https://github.com/searxng/searxng

## Citation

関連する作業において本プロジェクトの一部または全部を参照または引用する場合は、以下の情報を記載してください：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友好リンク

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
