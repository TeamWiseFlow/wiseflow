# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **4.x をお探しですか？** オリジナルの v4.30 以前のコードは [`4.x` ブランチ](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)にありま��。

```
「我が生には涯（かぎり）有るも、知には涯無し。涯有るを以て涯無きに随（したが）うは、殆（あやう）きのみ！」—— 『荘子・内篇・養生主第三』
```

wiseflow 4.x（およびそれ以前のバージョン）は、一連の精密なワークフローによって特定のシナリオで強力なデータ取得能力を実現しましたが、依然として多くの制限がありました：

- 1. インタラクティブなコンテンツを取得できない（クリックしないと表示されないコンテンツ、特に動的ロードの場合）
- 2. 情報のフィルタリングと抽出のみで、下流タスク処理能力がほぼない
- ……

私たちは機能の改善と範囲の拡大に取り組んできましたが、現実の世界は複雑であり、インターネットも同様です。ルールを網羅することは不可能であるため、固定のワークフローではすべてのシナリオに対応できません。これは wiseflow の問題ではなく、従来のソフトウェアの問題です！

しかし、この一年で Agent 技術が飛���的に進歩し、大規模言語モデルによって人間のインターネット行動を完全にシミュレートすることが技術的に可能であることが示されました。[openclaw](https://github.com/openclaw/openclaw) の登場は、この確信をさらに強めました。

さらに驚くべきことに、初期の実験と探索を通じて、wiseflow のデータ取得能力を「プラグイン」として openclaw に統合することで、上記の2つの制限を完全に解決できることを発見しました。

https://github.com/user-attachments/assets/8d097b3b-f9ab-42eb-98bb-88af5d28b089

ただし、openclaw のプラグインシステムは、従来の「プラグイン」（Claude Code のプラグインのようなもの）とは異なるため、「add-on」という概念を新たに導入する必要がありました。正確に言えば、wiseflow 5.x は openclaw の add-on として提供されます。オリジナルの openclaw には「add-on」アーキテクチャがありませんが、実際にはいくつかの簡単なシェルコマンドでこの「改造」を完了できます。また、実際のビジネスシーンに向���たプリセット設定を含む、すぐに使える openclaw 強化版 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business) も用意しています。クローンして、wiseflow のリリースを openclaw_for_business の add-on フォルダに配置するだけで使用できます。

## ✨ wiseflow をインストールすることで何が得られますか（オリジナル openclaw より優れている点）？

### 1. アンチ検出ブラウザ、ブラウザ拡張機能インストール不要

wiseflow の patch-001 は、openclaw に内蔵された Playwright を [Patchright](https://github.com/Kaliiiiiiiiii-Vinyzu/patchright)（Playwright の検出回避フォーク）に置き換え、自動化ブラウザがターゲットサイトに検出・ブロックされる可能性を大幅に低減します。これにより、Chrome Relay Extension をインストールすることなく、マネージドブラウザだけで Relay と同等、あるいはそれ以上のウェブ取得・操作能力を実現できます。

📥 *私たちは現在市場で人気のあるブラウザ自動化フレームワーク（nodriver、browser-use、Vercel の agent-browser など）を総合的に評価しました。すべてが CDP を通じて動作し、openclaw 専用の永続化プロファイルを提供するという基本原理は同じですが、CDP プローブの完全な除去を提供しているのは Patchright だけです。つまり、最も純粋な CDP 直接接続アプローチを使用しても、特徴的なフィンガープリントは残り、検出される可能性があります。他のフレームワークはデータ取得ではなく自動テストを目的として設計されていますが、Patchright はもともとデータ取得を目的として設計されており、本質的には Playwright のパッチであり、ほぼすべての Playwright の上位 API を継承しています。これにより openclaw とのネイティブな互換性が実現し、追加のプラグインや MCP をインストールする必要がありません。*

### 2. タブ自動復元メカニズム

Agent の操作中にターゲットタブが予期せず閉じられたり失われたりした場合、スナップショットベースのタブ復元を自動的に実行し、タブの消失によるタスクの中断を防ぎます。

### 3. スマート検索 Skill

openclaw に内蔵された `web_search` をより強力な検索機能に置き換えます。オリジナルの内蔵 web search tool と比較して、スマート検索には3つの主要な優位性があります：

- **完全無料、API キー不要**：サードパーティの検索 API に依存せず、ゼロコストで利用可能
- **リアルタイム検索、最高の鮮度**：ブラウザを直接ターゲットページや主要なソーシャルメディアプラットフォーム（Weibo、Twitter/X、Facebook など）に誘導し、最新公開コンテンツを即座に取得
- **検索ソースのカスタマイズ**：ユーザーが自由に検索ソースを指定でき、必要な情報を精確に取得

### 4. 新媒体小編 Crew（プリセット AI エージェント）

すぐに使える中国語ソーシャルメディアコンテンツ制作 AI エージェントで、微博、小紅書、知乎、B ステーション、抖音などの中国の主要プラットフォームに特化しています。

**主な機能：**

- テーマリサーチ + トレンド分析（モード A）
- 下書き拡充 + オンライン根拠追加（モード B）
- 記事確定後、[文颜（Wenyan）](https://github.com/caol64/wenyan) を自動呼び出して WeChat 公式アカウント形式の HTML にレンダリング（7 種類の内蔵テーマ対応）
- WeChat 公式アカウントの下書きに直接プッシュ（モード C、`WECHAT_APP_ID`/`WECHAT_APP_SECRET` の設定が必要）
- AI 画像/動画生成サポート（[SiliconFlow](https://www.siliconflow.com/) 画像/動画生成、`SILICONFLOW_API_KEY` の設定が必要）

## 🌟 クイックスタート

> **💡 API コストのご説明**
>
> wiseflow 5.x は openclaw の Agent ワークフローをベースにしており、LLM API アクセスが必要です。事前に API 資格情報を準備することをお勧めします：
>
> - **海外ユーザー（推奨）**：[SiliconFlow](https://www.siliconflow.com/) — 登録後に無料クレジットが付与され、初期使用コストをカバーできます
> - **OpenAI / Anthropic その他のプロバイダー**：互換性のある任意の API が使用可能です

本リポジトリの [Releases](https://github.com/TeamWiseFlow/wiseflow/releases) から openclaw_for_business と wiseflow addon を含む統合パッケージをダウンロードしてください。

1. アーカイブをダウンロードして解凍する
2. 解凍されたフォルダに移動する
3. 起動方式を選択する：

   **デバッグモード**（単回起動、テスト・開発向け）：
   ```bash
   ./scripts/dev.sh gateway
   ```

   **本番モード**（システムサービスとしてインストール、長期運用向け）：
   ```bash
   ./scripts/reinstall-daemon.sh
   ```

> **システム要件**
> - **Ubuntu 22.04** を推奨
> - **Windows WSL2** 環境をサポート
> - **macOS** をサポート
> - **Windows ネイティブ**環境での直接実行は**非対応**

### 【代替】手動インストール

> 注意：先に openclaw_for_business をダウンロード・デプロイする必要があります。ダウンロード先：https://github.com/TeamWiseFlow/openclaw_for_business/releases

本リポジトリ内の `wiseflow` フォルダ（リポジトリ全体ではありません）を openclaw_for_business の `addons/` ディレクトリにコピーしてください：

```bash
# 方法1：wiseflow リポジトリからクローン
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/wiseflow <openclaw_for_business>/addons/wiseflow
```

インストール後、openclaw_for_business を再起動すると有効になります。

## ディレクトリ構造

```
wiseflow/                         # addon パッケージ（addons/ ディレクトリに配置）
├── addon.json                    # メタデータ
├── overrides.sh                  # pnpm overrides + 内蔵 web_search を無効化
├── patches/
│   ├── 001-browser-tab-recovery.patch        # タブ復元パッチ
│   ├── 002-disable-web-search-env-var.patch  # 内蔵 web_search の無効化（env var）
│   └── 003-act-field-validation.patch        # ACT フィールド検証パッチ
├── skills/                       # グローバルスキル（全エージェント利用可能）
│   ├── browser-guide/SKILL.md    # ブラウザのベストプラクティス（ログイン/CAPTCHA/遅延ロードなど）
│   ├── smart-search/SKILL.md     # マルチプラットフォーム検索URL構築（内蔵 web_search の代替）
│   └── rss-reader/               # RSS/Atom フィードリーダー
│       ├── SKILL.md
│       ├── package.json
│       └── scripts/fetch-rss.mjs
└── crew/                         # プリセット AI エージェント（Crew テンプレート）
    └── new-media-editor/         # 新媒体小編（中国語ソーシャルメディアコンテンツ制作）
        ├── IDENTITY.md / SOUL.md / AGENTS.md / TOOLS.md / ...
        └── skills/               # Crew 専属スキル
            ├── siliconflow-img-gen/   # AI 画像生成（SiliconFlow API）
            ├── siliconflow-video-gen/ # AI 動画生成（SiliconFlow API）
            └── wenyan-formatter/      # Markdown → WeChat HTML / 下書きプッシュ

docs/                             # 技術ドキュメント（リポジトリルート）
├── anti-detection-research.md
└── more_powerful_search_skill/

scripts/                          # ユーティリティスクリプト（リポジトリルート）
└── generate-patch.sh

tests/                            # テストケースとスクリプト（リポジトリルート）
├── README.md
└── run-managed-tests.mjs
```

## WiseFlow Pro 版がリリースされました！

より強力なスクレイピング能力、より包括的なソーシャルメディアサポート、UI インターフェースとワンクリックインストールパッケージ付き — デプロイ不要！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 版が発売中**：https://shouxiqingbaoguan.com/

🌹 本日より、wiseflow オープンソース版への PR 貢献（コード、ドキュメント、成功事例の共有すべて歓迎）が採用された場合、コントリビューターには wiseflow Pro 版の1年間ライセンスが贈呈されます！

## 🛡️ ライセンス

バージョン 4.2 以降、オープンソースライセンスを更新しました。詳細はこちら：[LICENSE](LICENSE)

商用提携については **Email：zm.zhao@foxmail.com** までご連絡ください。

## 📬 お問い合わせ

ご質問やご提案がございましたら、[issue](https://github.com/TeamWiseFlow/wiseflow/issues) からお気軽にメッセージをお寄せください。

🎉 wiseflow && OFB では現在**有料ナレッジベース**を提供しています。内容には、ゼロからの手順インストールチュートリアル、各種独自の活用ノウハウ、および **VIP WeChat グループ**が含まれます：

ご相談は「掌柜的」企業 WeChat をご追加ください：

<img width="360" height="360" alt="wiseflow掌柜" src="https://github.com/user-attachments/assets/b013b3fd-546e-4176-b418-57bee419e761" />

🌹 オープンソース維持のご支援に感謝します！

## 🤝 wiseflow 5.x は以下の優秀なオープンソースプロジェクトを基盤としています：

- Patchright（Playwright テスト・自動化ライブラリの検出回避 Python 版）https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser（Python でフィードを解析）https://github.com/kurtmckee/feedparser
- SearXNG（様々な検索サービスやデータベースから結果を集約する無料のインターネットメタ検索エンジン）https://github.com/searxng/searxng
- 文颜（Wenyan）（多プラットフォーム Markdown フォーマットと投稿ツール、新媒体小編 Crew が wenyan-formatter スキル経由で使用）https://github.com/caol64/wenyan

## Citation

本プロジェクトの一部または全部を参照・引用する場合は、以下の情報を明記してください：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## パートナー

[<img src="https://github.com/TeamWiseFlow/wiseflow/raw/4.x/docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
