# AI チーフインテリジェンスオフィサー（Wiseflow）

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/TeamWiseFlow/wiseflow)

🚀 **大規模言語モデルを使用して、日々の膨大な情報や様々なソースから、あなたが本当に興味のある情報を掘り起こしましょう！**

私たちに不足しているのは情報ではなく、膨大な情報からノイズをフィルタリングし、価値のある情報を引き出す能力です。

## 🎉  WiseFlow Pro バージョンが利用可能になりました！

強化されたクローリング機能、包括的なソーシャルメディアサポート、UIインターフェース、ワンクリックインストールパッケージ！

https://github.com/user-attachments/assets/880af7a3-7b28-44ff-86b6-aaedecd22761

🔥🔥 **Proバージョンは世界中で利用可能です**：https://wiseflow.pro/ 

🔥 PR（コード、ドキュメント、または成功事例の共有）を提出する貢献者は、採用時にWiseFlow Proバージョンの1年間のアクセス（関連するLLM使用料を含む）を受け取ります！

## 🔥🔥🔥 Wiseflow 4.2 バージョンが正式にリリースされました！

バージョン4.2では、バージョン4.0、4.1を基盤にウェブクローリング機能を大幅に強化しました。プログラムは今、あなたのローカルの「本物の」Chrome ブラウザを直接呼び出してフェッチすることができます。これにより、ターゲットサイトによる「リスクコントロール」の確率を最大限に低減するだけでなく、永続的なユーザーデータやページ操作スクリプトのサポートなどの新機能ももたらします！（例えば、一部のウェブサイトではユーザーログイン後に完全なコンテンツを表示するため、事前にログインしてからwiseflowを使用して完全なコンテンツを取得できます）。

バージョン4.2ではローカルChromeブラウザを直接使用するため、デプロイ時に `python -m playwright install --with-deps chromium` を実行する必要がなくなりましたが、**デフォルトインストールパスでGoogle Chromeブラウザをインストールする必要があります**。

さらに、検索エンジンソリューションのリファクタリングと完全なプロキシソリューションも提供しました。詳細は **[CHANGELOG](CHANGELOG.md)** をご覧ください。

### 🔍 カスタム検索ソース

バージョン4.1では、フォーカスポイントごとに検索ソースを正確に設定できるようになりました。現在、bing、github、arxivの検索ソースをサポートしており、すべてプラットフォームのネイティブインターフェースを使用しているため、追加のサードパーティサービスを申請する必要はありません。

<img src="docs/select_search_source.gif" alt="search_source" width="360">


### 🧠 AIにあなたの立場で考えさせましょう！

バージョン4.1では、フォーカスポイントに役割と目的を設定して、LLMが特定の視点や目的で分析・抽出を行うように指導できます。ただし、使用する際には以下の点にご注意ください：

    - フォーカスポイント自体が非常に具体的な場合、役割と目的の設定が結果に与える影響はほとんどありません。
    - 最終的な結果の品質に最も影響を与える要素は常に情報源です。フォーカスポイントに非常に関連性の高い情報源を提供してください。

役割と目的の設定が抽出結果に与える影響に関するテストケースについては、[task1](test/reports/report_v4x_llm/task1)を参照してください。


### ⚙️ カスタム抽出モード

pbインターフェースで独自のフォームを作成し、特定のフォーカスポイントに設定できるようになりました。LLMはフォームのフィールドに従って正確に情報を抽出します。


### 👥 ソーシャルメディアソースのクリエーター検索モード

フォーカスポイントに基づいてソーシャルメディアプラットフォームで関連コンテンツを検索し、さらにコンテンツクリエーターのホームページ情報を見つけるようにプログラムを指定できるようになりました。「カスタム抽出モード」と組み合わせることで、wiseflowはネットワーク全体で潜在的な顧客、パートナー、または投資家の連絡先情報を検索するのに役立ちます。

<img src="docs/find_person_by_wiseflow.png" alt="find_person_by_wiseflow" width="720">


**バージョン4.1に関する詳細な更新情報については、[CHANGELOG](CHANGELOG.md)をご覧ください。**

## 🌹 最適なLLM組み合わせガイド

「LLM時代において、優秀な開発者は少なくとも時間6割を適切なLLMモデルの選択に費やすべきです」 ☺️

私たちは実际のプロジェクトから7つのテストサンプルを安選し、出力価格が￥4/Mトークンを超えない主流モデルを幅広く選択し、詳細なwiseflow情報抽出タスクテストを実行し、以下の使用推奨を得ました：

    - パフォーマンス優先シナリオでの推奨：ByteDance-Seed/Seed-OSS-36B-Instruct

    - コスト優先シナリオでは依然推奨：Qwen/Qwen3-14B

視覚補助分析モデルには依然使用可能：Qwen/Qwen2.5-VL-7B-Instruct（wiseflowタスクは現在これに対する依存度が低い）

詳細なテストレポートは[LLM USE TEST](./test/reports/README_EN.md)をご覧ください

以上のテスト結果はwiseflow情報抽出タスクにおけるモデルのパフォーマンスのみを表し、モデルの総合能力を表すものではありません。wiseflow情報抽出タスクと他のタイプのタスク（企画、執筆など）とは明らかに異なる可能性があります。また、wiseflowタスクはモデルの使用量消費が大きいため、特にマルチソース、マルチフォーカスシナリオでは、コストが重要な考慮事項の一つです。

wiseflowはモデルサービスプロバイダーを制限しません。openaiSDKリクエストインターフェース形式と互換性があれば、既存のMaaSサービスやOllamaなどのローカルデプロイモデルサービスを選択できます。

[Siliconflow](https://www.siliconflow.com/)のモデルサービスの使用を推奨します。

あるいは、openaiシリーズモデルをより好む場合、'o3-mini'や'openai/gpt-oss-20b'も良い選択であり、視覚補助分析はgpt-4o-miniと組み合わせることができます。

💰 現在、wiseflowアプリケーション内でAiHubMixが転送するOpenAIシリーズモデルの公式インターフェースを公式価格の9割で使用できます。

**注意：** 割引を享受するにはaihubmixブランチに切り替える必要があります。詳細は[README](https://github.com/TeamWiseFlow/wiseflow/blob/aihubmix/README.md)をご覧ください

## 🧐  "ChatGPTs" / "Deepseeks" / "豆包" などとの違い

まず、wiseflowはこれらの製品と同様に、背後にはLLM（大規模言語モデル）がありますが、設計目的が異なるため、以下の2つのシナリオでは、「ChatGPTs」/「Deepseeks」/「豆包」などを使用してもニーズを満たせない可能性があります（おそらく、現時点では、これらのニーズにwiseflowよりも適した製品は見つからないでしょう ☺️）

指定された信源から最新（数時間以内に公開）のコンテンツを取得する必要があり、興味のある部分を漏らしたくない場合

例えば、権威ある機関の政策発表の追跡、業界情報や技術情報の追跡、競合他社の動向の追跡、または限られた高品質な信源から情報を取得したい場合（推薦アルゴリズムの支配から解放されたい🤣）など...「ChatGPTs」/「Deepseeks」/「豆包」などの汎用Q&Aエージェントは、指定された信源を監視しません。それらは検索エンジンのように機能し、ネットワーク全体の情報を対象とし、通常2〜3日またはそれ以上の遅延がある「二次情報」しか取得できません。

ネットワーク（特にソーシャルメディア）から繰り返し指定された情報を発見し、抽出する必要がある場合

例えば、ソーシャルメディアから特定の分野の潜在的な顧客、サプライヤー、または投資家を見つけ、連絡先情報を収集するなど...同様に、「ChatGPTs」/「Deepseeks」/「豆包」などの汎用Q&Aエージェントは、答えを要約し、精緻化することに長けていますが、情報を収集し、整理することには長けていません。

## ✋ 「クローラー」やRPAとの違い

まず、wiseflowはクローラーではなく、従来の意味でのRPAでもありません！

Wiseflowは、あなたのブラウザを使用して、実際の人間の行動であなたに代わって操作します（もちろん、これはLLM、さらには視覚LLMに依存しています）。このプロセスには非準拠の行動はありません。すべてのログインおよび検証操作について、wiseflowはユーザーに通知するだけで、越権行為はしません。もちろん、有効期間中はこれらの操作を1回だけ実行すればよく、wiseflowはログイン状態を保持します（ただし、ユーザー名とパスワードは保持しません。実際、wiseflowは入力したユーザー名やパスワードを一切読み取ることができません。すべての操作は実際の公式ページで実行されます）。

Wiseflowは実際のブラウザ（ヘッドレスブラウザ、仮想ブラウザなどではなく）を使用し、実際のユーザーの閲覧行動を完全にシミュレートするため、「クローラー」やRPAよりも強力な検出回避機能を備えています。さらに、以下の機能があります：

- フルプラットフォーム取得機能：ウェブサイト、RSS、微博、快手、Bing、GitHub、arXiv、eBayなどをサポート。Pro版はさらに微信公式アカウント、小红书、知乎、B站、抖音をサポート。
- 革新的なHTMLインテリジェント解析メカニズム：重要な情報とさらに探索する価値のあるリンクを自動的に識別できます。
- 「クロールと検索を一体化」戦略：クロール中にリアルタイムでLLMが判断と抽出を行い、関連情報のみをキャプチャし、リスク制御リスクを大幅に削減します。
- 真にすぐに使用可能：Xpath、スクリプト、または手動設定は不要。一般ユーザーでも簡単に使用できます。
- LLM使用料を全く心配する必要がありません：すべてのLLM呼び出し料金はサブスクリプションに含まれており、サービスやキーを個別に設定する必要はありません。

## 🌟 クイックスタート

**たった3ステップで始められます！**

**Windowsユーザーは事前にGit Bashツールをダウンロードし、bashで以下のコマンドを実行してください [Bashダウンロードリンク](https://git-scm.com/downloads/win)**

**4.2バージョン以降、まずGoogle Chromeブラウザをインストールする必要があります（デフォルトインストールパスを使用）**

### 📋 プロジェクトのソースコードをダウンロードし、uvとpocketbaseをインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

上記の操作でuvのインストールが完了します。

次に、[pocketbase docs](https://pocketbase.io/docs/)からお使いのシステムに対応するpocketbaseプログラムをダウンロードし、[.pb](./pb/)フォルダに配置してください。

install_pocketbase.sh（MacOS/Linux用）またはinstall_pocketbase.ps1（Windows用）を使用してインストールすることもできます。

### 📥 env_sampleを参考に.envファイルを設定

wiseflowフォルダ（プロジェクトのルートディレクトリ）でenv_sampleを参考に.envファイルを作成し、関連する設定情報を入力してください

4.x バージョンでは、ユーザーが .env ファイルに pocketbase の認証情報を提供する必要がなく、pocketbase のバージョンにも制限がなくなりました。また、セカンダリモデルの設定も一時的に削除されたため、実質的に最小限の4つのパラメーターで設定を完了できます：

- LLM_API_KEY="" # LLM サービスのキー (すべての OpenAI 形式 API を提供するモデル サービスを使用できます。ローカルで ollama を使用してデプロイする場合は設定する必要はありません)
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLM サービスインターフェースアドレス（siliconflowサービスの使用を推奨、私の [推奨リンク](https://cloud.siliconflow.cn/i/WNLYbBpi) を使用して申請していただけると、私たち両方とも￥14のプラットフォーム報酬を獲得できます🌹）
- PRIMARY_MODEL=ByteDance-Seed/Seed-OSS-36B-Instruct # 価格敏感であまり複雑でない抽出シナリオでは Qwen3-14B を使用できます
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # あったほうが良い

### 🚀 起動！

```bash
cd wiseflow
uv venv # 初回実行時のみ必要
source .venv/bin/activate  # Linux/macOS
# または Windows 上：
# .venv\Scripts\activate
uv sync # 初回実行時のみ必要
chmod +x run.sh # 初回実行時のみ必要
./run.sh  # Linux/macOS
.\run.bat  # Windows
```

詳細な使用方法については、[docs/manual/manual_ja.md](./docs/manual/manual_ja.md)を参照してください

## 📚 Wiseflowでクロールしたデータを自分のプログラムで使用する方法

Wiseflowでクロールしたすべてのデータは即座にpocketbaseに保存されるため、pocketbaseデータベースを直接操作してデータを取得できます。

人気のある軽量データベースとして、PocketBaseは現在Go/Javascript/Pythonなどの言語のSDKを提供しています。

以下のリポジトリで、あなたの二次開発アプリケーションの事例を共有し、宣伝していただくことを歓迎します！

- https://github.com/TeamWiseFlow/wiseflow-plus

（このリポジトリへのPRの貢献も、採用時にWiseFlow Proバージョンの1年間のアクセスを付与します）

## 🛡️ ライセンス

4.2バージョン以降、オープンソースライセンス契約を更新しました。詳細は [LICENSE](LICENSE) をご確認ください。

商用協力については、**Email: zm.zhao@foxmail.com**までご連絡ください

## 📬 連絡先

ご質問やご提案がありましたら、[issue](https://github.com/TeamWiseFlow/wiseflow/issues)を通じてメッセージを残してください。

## 🤝 このプロジェクトは以下の優れたオープンソースプロジェクトに基づいています：

- Crawl4ai（オープンソースLLMフレンドリーウェブクローラー＆スクレイパー）https://github.com/unclecode/crawl4ai
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihuクローラー）https://github.com/NanmiCoder/MediaCrawler
- Patchright(Undetected Python version of the Playwright testing and automation library) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright-python
- NoDriver（ウェブ自動化、ウェブスクレイピング、ボット、その他の創造的なアイデアのための高速フレームワークを提供）https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase（1ファイルのオープンソースリアルタイムバックエンド）https://github.com/pocketbase/pocketbase
- Feedparser（Pythonでフィードを解析）https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## 引用

関連する作業でこのプロジェクトの一部または全部を参照または引用する場合は、以下の情報を記載してください：

```
著者：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
```

## 友好リンク

[<img src="docs/logos/SiliconFlow.png" alt="siliconflow" width="360">](https://siliconflow.com/)