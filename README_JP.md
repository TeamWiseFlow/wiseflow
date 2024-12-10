# 首席情報官（Wiseflow）

**[English](README_EN.md) | [简体中文](README.md) | [한국어](README_KR.md)**

🚀 **首席情報官**（Wiseflow）は、ウェブサイト、微信公衆号、ソーシャルプラットフォームなど、さまざまな情報源から設定された関心事に基づいて情報を抽出し、自動的にタグ付けしてデータベースにアップロードする、アジャイルな情報マイニングツールです。

**私たちが欠けているのは情報ではなく、大量の情報からノイズをフィルタリングし、価値ある情報を明らかにすることです**

🌱首席情報官がどのようにあなたの時間を節約し、無関係な情報をフィルタリングし、関心のあるポイントを整理するのかを見てみましょう！🌱

https://github.com/user-attachments/assets/f6fec29f-2b4b-40f8-8676-8433abb086a7

## 🔥 V0.3.5 バージョンの隆盛な紹介

コミュニティのフィードバックを十分に聞き取り、wiseflowの製品ポジションを再検討し、新しいポジションはより焦点を絞り込んでいます。V0.3.5バージョンは、この新しいポジションの下での新しいアーキテクチャバージョンです。

- 基礎的なクローラーおよびタスク管理フレームワークとして [Crawlee](https://github.com/apify/crawlee-python) を導入し、ページ取得能力を大幅に向上させました。以前に取得できなかった（または取得が文字化けした）ページも現在は良好に取得できるようになりました。今後、良好に取得できないページがあれば、[issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136) でフィードバックをお願いします；
- 新しい製品ポジション下での新しい情報抽出戦略——「クロールと検査の一体化」、記事の詳細抽出を放棄し、クロール過程でLLMを直接使用してユーザーが関心を持つ情報（infos）を抽出し、追跡が必要なリンクを自動的に判断します。**あなたが関心を持つことがあなたが必要なことです**；
- 最新バージョン（v0.23.4）のPocketbaseに適合し、フォーム設定を更新しました。また、新しいアーキテクチャではGNEなどのモジュールが不要になり、requirement依存項目が8つに減少しました；
- 新しいアーキテクチャのデプロイメントソリューションもより簡単になり、dockerモードでコードリポジトリのホットアップデートをサポートします。これは、今後のアップグレードでdocker buildを繰り返す必要がなくなることを意味します。
- 詳細は [CHANGELOG](CHANGELOG.md) を参照してください

🌟 **V0.3.x 今後の計画**

- [SeeAct](https://github.com/OSU-NLP-Group/SeeAct) ソリューションを導入し、視覚大モデルを使用して複雑なページの操作をガイドします。例えば、スクロール、クリック後に情報が表示される場合など（V0.3.6）；
- 微信公众号のwxbotなしのサブスクリプションをサポートすることを試みます（V0.3.7）；
- RSS情報源のサポートを導入します（V0.3.8）；
- LLM駆動の軽量な知識グラフを導入し、ユーザーがinfosから洞察を得るのを助けます（V0.3.9）。

## ✋ wiseflow と従来のクローラーツール、AI検索、知識ベース（RAG）プロジェクトの違いは何ですか？

wiseflowは2024年6月末にV0.3.0バージョンをリリースして以来、オープンソースコミュニティから広く注目を集めており、さらに多くのメディアが自発的に報道してくれました。ここでまず感謝の意を表します！

しかし、私たちは一部の関心者がwiseflowの機能ポジションについていくつかの理解のズレを持っていることに気づきました。以下の表は、従来のクローラーツール、AI検索、知識ベース（RAG）類プロジェクトとの比較を通じて、wiseflowの最新の製品ポジションについての私たちの考えを表しています。

|          | **首席情報官（Wiseflow）** との比較説明| 
|-------------|-----------------|
| **クローラーツール** | まず、wiseflowはクローラーツールに基づくプロジェクトです（現在のバージョンでは、クローラーフレームワークCrawleeを基にしています）。しかし、従来のクローラーツールは情報抽出において人間の介入が必要で、明確なXpathなどを提供する必要があります……これは一般ユーザーを妨げるだけでなく、汎用性も全くありません。異なるウェブサイト（既存のウェブサイトのアップグレード後を含む）ごとに人間が再分析し、抽出コードを更新する必要があります。wiseflowはLLMを使用してウェブページの分析と抽出を自動化することを目指しており、ユーザーはプログラムに関心事を伝えるだけで済みます。この観点から、wiseflowは「自動的にクローラーツールを使用できるAIエージェント」と簡単に理解できます |
| **AI検索** | AI検索の主なアプリケーションシナリオは**具体的な問題の即時回答**です。例：「XX社の創設者は誰ですか」、「xxブランドのxx製品はどこで販売されていますか」。ユーザーが求めているのは**一つの答え**です；wiseflowの主なアプリケーションシナリオは**ある方面の情報の継続的な収集**です。例えば、XX社の関連情報の追跡、XXブランドの市場行動の継続的な追跡……これらのシナリオでは、ユーザーは関心事（ある会社、あるブランド）、さらには情報源（サイトURLなど）を提供できますが、具体的な検索問題を提起することはできません。ユーザーが求めているのは**一連の関連情報**です| 
| **知識ベース（RAG）類プロジェクト** | 知識ベース（RAG）類プロジェクトは通常、既存の情報に基づく下流タスクであり、一般的にプライベート知識（例えば、企業内の操作マニュアル、製品マニュアル、政府部門の文書など）を対象としています；wiseflowは現在、下流タスクを統合しておらず、インターネット上の公開情報を対象としています。「エージェント」の観点から見ると、両者は異なる目的のために構築されたエージェントであり、RAG類プロジェクトは「（内部）知識アシスタントエージェント」であり、wiseflowは「（外部）情報収集エージェント」です|

## 📥 インストールと使用

### 1. コードリポジトリのクローン

🌹 いいね、forkは良い習慣です 🌹

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. env_sample を参考に .env ファイルを core ディレクトリに配置

🌟 **ここは以前のバージョンと異なります**。V0.3.5からは .env を coreフォルダに配置する必要があります。

また、V0.3.5からenv設定が大幅に簡素化され、必須の設定項目は3つだけです。具体的には以下の通り：

- LLM_API_KEY=""

    大モデルサービスのキーで、これは必須です

- LLM_API_BASE="https://api.siliconflow.cn/v1" 

    サービスインターフェースのアドレスで、openai sdk をサポートする任意のサービスプロバイダーを使用できます。直接openaiのサービスを使用する場合、この項目は記入不要です

- PB_API_AUTH="test@example.com|1234567890" 

  pocketbase データベースの superuser ユーザー名とパスワードで、| で区切ってください

以下はオプションの設定です：
- #VERBOSE="true" 

  観測モードを有効にするかどうかで、有効にすると、debug log情報がloggerファイルに記録されます（デフォルトではconsoleにのみ出力されます）。また、playwrightのブラウザウィンドウが開き、クロールプロセスを観察しやすくなります；

- #PRIMARY_MODEL="Qwen/Qwen2.5-7B-Instruct"

    主モデルの選択で、siliconflowサービスを使用する場合、この項目を記入しないとデフォルトでQwen2.5-7B-Instructが呼び出されます。実測では基本的に十分ですが、より**Qwen2.5-14B-Instructを推奨**します

- #SECONDARY_MODEL="THUDM/glm-4-9b-chat" 

    副モデルの選択で、siliconflowサービスを使用する場合、この項目を記入しないとデフォルトでglm-4-9b-chatが呼び出されます。

- #PROJECT_DIR="work_dir" 

    プロジェクト実行データのディレクトリで、設定しない場合、デフォルトで `core/work_dir` になります。注意：現在、coreディレクトリ全体がcontainerにマウントされているため、ここに直接アクセスできます。

- #PB_API_BASE="" 

  pocketbaseがデフォルトのIPまたはポートで実行されていない場合にのみ設定が必要で、デフォルトの場合は無視してください。

### 3.1 dockerを使用して実行

✋ V0.3.5バージョンのアーキテクチャと依存関係は以前のバージョンと大きく異なるため、必ずコードを再取得し、古いバージョンのイメージ（pb_dataフォルダを含む）を削除し、再構築してください！


```bash
cd wiseflow
docker compose up
```

**注意：**

初めてdocker containerを実行すると、プログラムがエラーを報告する可能性があります。これは正常な現象です。画面の指示に従ってsuper userアカウントを作成してください（必ずメールアドレスを使用してください）。そして、作成したユーザー名とパスワードを.envファイルに記入し、containerを再起動してください。

🌟 dockerソリューションはデフォルトで task.py を実行します。つまり、定期的にクロール-抽出タスクを実行します（起動時にすぐに1回実行され、その後1時間ごとに1回起動されます）

### 3.2 python環境を使用して実行

✋ V0.3.5バージョンのアーキテクチャと依存関係は以前のバージョンと大きく異なるため、必ずコードを再取得し、pb_dataを削除（または再構築）してください

condaを使用して仮想環境を構築することをお勧めします

```bash
cd wiseflow
conda create -n wiseflow python=3.10
conda activate wiseflow
cd core
pip install -r requirements.txt
```

その後、ここ [ダウンロード](https://pocketbase.io/docs/) から対応するpocketbaseクライアントを取得し、[/pb](/pb) ディレクトリに配置します。そして

```bash
chmod +x run.sh
./run_task.sh # もしサイトを1回だけスキャンしたい場合（ループなし）、./run.sh を使用してください
```

このスクリプトは、pocketbaseがすでに実行中かどうかを自動的に判断します。実行中でない場合、自動的に起動します。ただし、ctrl+cまたはctrl+zでプロセスを終了した場合、pocketbaseプロセスは終了せず、terminalを閉じるまで続行されます。

また、dockerデプロイと同様に、初回実行時にエラーが発生する可能性があります。画面の指示に従ってsuper userアカウントを作成してください（必ずメールアドレスを使用してください）。そして、作成したユーザー名とパスワードを.envファイルに記入し、再度実行してください。

もちろん、別のterminalで事前にpocketbaseを実行して設定することもできます（これにより初回のエラーを回避できます）。具体的には [pb/README.md](/pb/README.md) を参照してください

### 4. モデル推奨 [2024-12-09]

モデルのパラメータ数が多いほど、より優れた性能を意味しますが、実測では**Qwen2.5-7b-Instructとglm-4-9b-chatモデルを使用するだけで基本的な効果を得られる**ことがわかりました。ただし、コスト、速度、効果を総合的に考慮すると、主モデル
**（PRIMARY_MODEL）にQwen2.5-14B-Instructを使用することをより推奨します**。

ここでは、siliconflow（シリコンフロー）のMaaSサービスを強く推奨します。複数の主流オープンソースモデルのサービスを提供し、大量のトークンを提供します。Qwen2.5-7b-Instructとglm-4-9b-chatは現在無料で提供されています。（主モデルにQwen2.5-14B-Instructを使用した場合、374ページをクロールし、43件のinfoを有効に抽出し、総コスト￥3.07）
      
😄 もしよろしければ、私の[siliconflow招待リンク](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)を使用してください。そうすれば、私もより多くのトークンを獲得できます 🌹

**もしあなたの情報源が主に非中国語のページであり、抽出されたinfoを中国語にする必要がない場合、openaiやclaudeなどの海外メーカーのモデルを使用することをより推奨します。**
   
サードパーティのプロキシ **AiHubMix** を試すことができます。OpenAI、Claude、Google、Llamaなどの幅広い主要なAIモデルに、たった1つのAPIでシームレスにアクセスできます。；

😄 以下の招待リンク [AiHubMix招待リンク](https://aihubmix.com?aff=Gp54) を使用して登録してください 🌹

🌟 **wiseflow自体はどのモデルサービスにも限定されておらず、openAI SDKと互換性のあるサービスであれば、ローカルにデプロイされたollama、Xinferenceなどのサービスも含まれます**


### 5. **関心事と定期的なスキャン情報源の追加**
    
プログラムを起動した後、pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/) を開きます
    
#### 5.1 focus_point フォームを開く

このフォームを使用して、あなたの関心事を指定できます。LLMはこれに基づいて情報を抽出、フィルタリング、分類します。
    
フィールド説明：
- focuspoint, 関心事の説明（必須）、例えば「上海の小学校から中学校への情報」、「暗号通貨価格」
- explanation，関心事の詳細な説明または具体的な約束、例えば「上海市公式発表の中学校進学情報のみ」、「BTC、ETHの現在価格、変動率データ」など
- activated, 有効化するかどうか。無効にするとこの関心事は無視され、無効にした後再び有効にできます。

注意：focus_pointの更新設定（activatedの調整を含む）後、**プログラムを再起動する必要があります。**

#### 5.2 sitesフォームを開く

このフォームを使用して、カスタム情報源を指定できます。システムはバックグラウンドで定期的なタスクを開始し、ローカルで情報源のスキャン、解析、分析を実行します。

sitesフィールド説明：
- url, 情報源のurlで、情報源は具体的な記事ページを指定する必要はありません。記事リストページを指定するだけで十分です。
- per_hours, スキャン頻度で、単位は時間、整数型（1~24の範囲、スキャン頻度は1日1回を超えないように、つまり24に設定することをお勧めします）
- activated, 有効化するかどうか。無効にするとこの情報源は無視され、無効にした後再び有効にできます。

**sitesの設定調整は、プログラムを再起動する必要はありません。**


## 📚 あなた自身のプログラムでwiseflowがクロールしたデータをどのように使用するか

1、[dashbord](dashboard) 部分のソースコードを参考に二次開発してください。

wiseflowのcore部分はdashboardを必要としません。現在の製品はdashboardを統合していません。もしdashboardが必要な場合、[V0.2.1バージョン](https://github.com/TeamWiseFlow/wiseflow/releases/tag/V0.2.1)をダウンロードしてください

2、直接Pocketbaseからデータを取得します

wiseflowがクロールしたすべてのデータは即座にpocketbaseに保存されるため、直接pocketbaseデータベースを操作してデータを取得できます。

PocketBaseは人気のある軽量データベースで、現在Go/Javascript/Pythonなどの言語のSDKがあります。
   - Go : https://pocketbase.io/docs/go-overview/
   - Javascript : https://pocketbase.io/docs/js-overview/
   - python : https://github.com/vaphes/pocketbase

## 🛡️ ライセンス

本プロジェクトは [Apache2.0](LICENSE) オープンソースライセンスに基づいています。

商用およびカスタムコラボレーションについては、**Email：35252986@qq.com** までお問い合わせください

- 商用顧客は私たちに報告登録をお願いします。製品は永遠に無料で提供されることを約束します。


## 📬 連絡先

何か質問や提案があれば、[issue](https://github.com/TeamWiseFlow/wiseflow/issues) でメッセージを残してください。


## 🤝 本プロジェクトは以下の優れたオープンソースプロジェクトに基づいています：

- crawlee-python （A web scraping and browser automation library for Python to build reliable crawlers. Works with BeautifulSoup, Playwright, and raw HTTP. Both headful and headless mode. With proxy rotation.） https://github.com/apify/crawlee-python
- json_repair（Repair invalid JSON documents ） https://github.com/josdejong/jsonrepair/tree/main 
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- SeeAct（a system for generalist web agents that autonomously carry out tasks on any given website, with a focus on large multimodal models (LMMs) such as GPT-4Vision.） https://github.com/OSU-NLP-Group/SeeAct

また、[GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler) からもインスピレーションを受けています。

## Citation

もしあなたが関連する作業で本プロジェクトの一部または全部を参照または引用した場合、以下の情報を記載してください：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```