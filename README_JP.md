# AI チーフインテリジェンスオフィサー（Wiseflow）

**[简体中文](README.md) | [English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md) | [العربية](README_AR.md)**

🚀 **大規模言語モデルを使用して、日々の膨大な情報や様々なソースから、あなたが本当に興味のある情報を掘り起こしましょう！**

私たちに不足しているのは情報ではなく、膨大な情報からノイズをフィルタリングし、価値のある情報を引き出す能力です。

https://github.com/user-attachments/assets/2c52c010-6ae7-47f4-bc1c-5880c4bd76f3

## 🔥🔥🔥 Wiseflow 4.1 バージョンが正式にリリースされました！

バージョン4.1では、バージョン4.0を基盤として、さらに多くのエキサイティングな新機能が追加されました！

### 🔍 カスタム検索ソース

バージョン4.1では、フォーカスポイントごとに検索ソースを正確に設定できるようになりました。現在、bing、github、arxiv、ebayの4つの検索ソースをサポートしており、すべてプラットフォームのネイティブインターフェースを使用しているため、追加のサードパーティサービスを申請する必要はありません。

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

## 🧐 'ディープサーチ' VS 'ワイドサーチ'

私はWiseflowを「ワイドサーチ」として位置づけています。これは現在人気の「ディープサーチ」と対比されるものです。

具体的には、「ディープサーチ」は特定の質問に対してLLMが自律的に検索パスを計画し、異なるページを継続的に探索し、十分な情報を収集して回答やレポートを生成するものです。しかし、時には特定の質問を持たずに検索し、深い探索も必要とせず、広範な情報収集（業界インテリジェンス収集、背景情報収集、顧客情報収集など）だけが必要な場合があります。このような場合、広さが明らかに意味を持ちます。「ディープサーチ」でもこのタスクを達成できますが、それは大砲で蚊を打つようなもので、非効率で高コストです。Wiseflowはまさにこの「ワイドサーチ」シナリオのために特別に設計されたツールです。

## ✋ Wiseflowが他のAI駆動クローラーと異なる点は？

- ウェブページ、ソーシャルメディア（現在WeiboとKuaishouプラットフォームをサポート）、RSSソース、さらにBing、GitHub、arXiv、eBay などの検索ソースを含む、フルプラットフォームの取得能力
- 独自のHTML処理ワークフローにより、注目点に基づいて情報を自動抽出し、さらなる探索に値するリンクを発見、14bパラメータのLLMで十分に機能
- ユーザーフレンドリー（開発者だけでなく）、Xpathなどの手動設定不要、「すぐに使える」
- 継続的なイテレーションによる高い安定性と可用性、システムリソースと速度のバランスを考慮した処理効率
- 単なる「クローラー」にとどまらない……

<img src="docs/wiseflow4.xscope.png" alt="4.x full scope" width="720">

(4.xアーキテクチャ全体計画図。破線枠内は未完成の部分です。能力のあるコミュニティ開発者が私たちに参加し、PRを貢献してくれることを願っています。すべての貢献者にはPro版の無料使用権が付与されます！)

## 🌟 クイックスタート

**たった3ステップで始められます！**

**Windowsユーザーは事前にGit Bashツールをダウンロードし、bashで以下のコマンドを実行してください [Bashダウンロードリンク](https://git-scm.com/downloads/win)**·

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
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLM サービス インターフェース アドレス
- PRIMARY_MODEL=Qwen/Qwen3-14B # 推奨 Qwen3-14B または同等の思考モデル
- VL_MODEL=Pro/Qwen/Qwen2.5-VL-7B-Instruct # あったほうが良い

### 🚀 起動！

```bash
cd wiseflow
uv venv # 初回実行時のみ必要
source .venv/bin/activate  # Linux/macOS
# または Windows 上：
# .venv\Scripts\activate
uv sync # 初回実行時のみ必要
python -m playwright install --with-deps chromium # 初回実行時のみ必要
chmod +x run.sh # 初回実行時のみ必要
./run.sh
```

詳細な使用方法については、[docs/manual/manual_ja.md](./docs/manual/manual_ja.md)を参照してください

## 📚 Wiseflowでクロールしたデータを自分のプログラムで使用する方法

Wiseflowでクロールしたすべてのデータは即座にpocketbaseに保存されるため、pocketbaseデータベースを直接操作してデータを取得できます。

人気のある軽量データベースとして、PocketBaseは現在Go/Javascript/Pythonなどの言語のSDKを提供しています。

以下のリポジトリで、あなたの二次開発アプリケーションの事例を共有し、宣伝していただくことを歓迎します！

- https://github.com/TeamWiseFlow/wiseflow_plus

## 🛡️ ライセンス

このプロジェクトは[Apache2.0](LICENSE)の下でオープンソースです。

商用協力については、**Email: zm.zhao@foxmail.com**までご連絡ください

- 商用顧客は登録のためにご連絡ください。オープンソースバージョンは永久に無料であることを約束します。

## 📬 連絡先

ご質問やご提案がありましたら、[issue](https://github.com/TeamWiseFlow/wiseflow/issues)を通じてメッセージを残してください。

## 🤝 このプロジェクトは以下の優れたオープンソースプロジェクトに基づいています：

- Crawl4ai（オープンソースLLMフレンドリーウェブクローラー＆スクレイパー）https://github.com/unclecode/crawl4ai
- MediaCrawler（xhs/dy/wb/ks/bilibili/zhihuクローラー）https://github.com/NanmiCoder/MediaCrawler
- NoDriver（ウェブ自動化、ウェブスクレイピング、ボット、その他の創造的なアイデアのための高速フレームワークを提供）https://github.com/ultrafunkamsterdam/nodriver
- Pocketbase（1ファイルのオープンソースリアルタイムバックエンド）https://github.com/pocketbase/pocketbase
- Feedparser（Pythonでフィードを解析）https://github.com/kurtmckee/feedparser
- SearXNG（a free internet metasearch engine which aggregates results from various search services and databases） https://github.com/searxng/searxng

## 引用

関連する作業でこのプロジェクトの一部または全部を参照または引用する場合は、以下の情報を記載してください：

```
著者：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Apache2.0ライセンス
```

## 友好リンク

[<img src="docs/logo/siliconflow.png" alt="siliconflow" width="360">](https://siliconflow.com/)