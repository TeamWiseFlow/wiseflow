# Wiseflow

**[中文](README.md) | [English](README_EN.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **STEP INTO 5.x**

> 📌 **4.x をお探しですか？** オリジナルの v4.30 以前のコードは [`4.x` ブランチ](https://github.com/TeamWiseFlow/wiseflow/tree/4.x)にあります。

```
「我が生には涯（かぎり）有るも、知には涯無し。涯有るを以て涯無きに随（したが）うは、殆（あやう）きのみ！」—— 『荘子・内篇・養生主第三』
```

wiseflow 4.x（およびそれ以前のバージョン）は、一連の精密なワークフローによって特定のシナリオで強力なデータ取得能力を実現しましたが、依然として多くの制限がありました：

- 1. インタラクティブなコンテンツを取得できない（クリックしないと表示されないコンテンツ、特に動的ロードの場合）
- 2. 情報のフィルタリングと抽出��みで、下流タスク処理能力がほぼない
- ……

私たちは機能の改善と範囲の拡大に取り組んできましたが、現実の世界は複雑であり、インターネットも同様です。ルールを網羅することは不可能であるため、固定のワークフローではすべてのシナリオに対応できません。これは wiseflow の問題ではなく、従来のソフトウェアの問題です！

しかし、この一年で Agent 技術が飛躍的に進歩し、大規模言語モデルによって人間のインターネット行動を完全にシミュレートすることが技術的に可能であることが示されました。[openclaw](https://github.com/openclaw/openclaw) の登場は、この確信をさらに強めました。

さらに驚くべきことに、初期の実験と探索を通じて、wiseflow のデータ取得能力を「プラグイン」として openclaw に統合することで、上記の2つの制限を完全に解決できることを発見しました。今後、エキサイティングな実際のデモ動画を順次公開するとともに、これらの「プラグイン」をオープンソースとしてリリースします。

ただし、openclaw のプラグインシステムは、従来の「��ラグイン」（Claude Code のプラグインのようなもの）とは異なるため、「add-on」という概念を新たに導入する必要がありました。正確に言えば、wiseflow 5.x は openclaw の add-on として提供されます。オリジナルの openclaw には「add-on」アーキテクチャがありませんが、実際にはいくつかの簡単なシェルコマンドでこの「改造」を完了できます。また、実際のビジネスシーンに向けたプリセット設定を含む、すぐに使える openclaw 強化版 [openclaw_for_business](https://github.com/TeamWiseFlow/openclaw_for_business) も用意しています。クローンして、wiseflow のリリースを openclaw_for_business の add-on フォルダに配置するだけで使用できます。

## 🌟 クイックスタート

このディレクトリを openclaw_for_business の `addons/` ディレクトリにコピーしてください：

```bash
# 方法1：wiseflow リポジトリからクローン
git clone https://github.com/TeamWiseFlow/wiseflow.git /tmp/wiseflow
cp -r /tmp/wiseflow/addon <openclaw_for_business>/addons/wiseflow

# 方法2：既に wiseflow リポジトリがある場合
https://github.com/TeamWiseFlow/wiseflow/releases から最新リリースをダウンロード
解凍して <openclaw_for_business>/addons に配置
```

インストール後、openclaw を再起動すると有効になります。

## ディレクトリ構造

```
addon/
├── addon.json                    # メタデータ
├── overrides.sh                  # pnpm overrides: playwright-core → patchright-core
├── patches/
│   └── 001-browser-tab-recovery.patch  # タブ復元パッチ
├── skills/
│   └── browser-guide/SKILL.md    # ブラウザ使用のベストプラクティス
├── docs/                         # 技術ドキュメント
│   ├── anti-detection-research.md
│   └── openclaw-extension-architecture.md
└── tests/                        # テストケースとスクリプト
    ├── README.md
    └── run-managed-tests.mjs
```

## WiseFlow Pro 版がリリースされました！

より強力なスクレイピング能力、より包括的なソーシャルメディアサポート、UI インターフェースとワンクリックインストールパッケージ付き — デプロイ不要！

https://github.com/user-attachments/assets/57f8569c-e20a-4564-a669-1200d56c5725

🔥 **Pro 版が発売中**：https://shouxiqingbaoguan.com/

🌹 本日より、wiseflow オープンソース版への PR 貢献（コード、ドキュメント、成功事例の共有すべて歓迎）が採用された場合、コントリビューターには wiseflow Pro 版の1年間ライセンスが贈呈されます！

📥 🎉 📚

## 🛡️ ラ���センス

バージョン 4.2 以降、オープンソースライセンスを更新しました。詳細はこちら：[LICENSE](LICENSE)

商用提携については **Email：zm.zhao@foxmail.com** までご連絡ください。

## 📬 お問い合わせ

ご質問やご提案がございましたら、[issue](https://github.com/TeamWiseFlow/wiseflow/issues) からお気軽にメッセージをお寄せください。

Pro 版に関するご要望や提携のフィードバックは、WeChat でお問い合わせください：

<img src="docs/wechat.jpg" alt="wechat" width="360">

## 🤝 wiseflow 5.x は以下の優秀なオープンソースプロジェクトを基盤としています：

- Patchright（Playwright テスト・自動化ライブラリの検出回避 Python 版）https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- Feedparser（Python でフィードを解析）https://github.com/kurtmckee/feedparser
- SearXNG（様々な検索サービスやデータベースから結果を集約する無料のインターネットメタ検索エンジン）https://github.com/searxng/searxng

## Citation

本プロジェクトの一部または全部を参照・引用する場合は、以下の情報を明記してください：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## パートナー

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)
