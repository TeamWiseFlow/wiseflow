# 首席情報官（Wiseflow）

**[English](README_EN.md) | [简体中文](README.md) | [한국어](README_KR.md)**

🚀 **首席情報官**（Wiseflow）は、大規模言語モデルの思考・分析能力を活用して、様々な情報源から特定の情報を正確に抽出できる俊敏な情報マイニングツールです。プロセス全体で人間の介入を必要としません。

**私たちが欠けているのは情報ではなく、大量の情報からノイズをフィルタリングし、価値ある情報を明らかにすることです**

🌱首席情報官がどのようにあなたの時間を節約し、無関係な情報をフィルタリングし、関心のあるポイントを整理するのかを見てみましょう！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥 テストスクリプトとテストレポートの公開

siliconflowが提供するdeepseekV2.5、Qwen2.5-32B-Instruct、Qwen2.5-14B-Instruct、Qwen2.5-coder-7B-Instructモデルの性能を、4つの実際のケースタスクと合計10の実際のウェブページサンプルで横断的にテストし比較しました。
テスト結果は[report](./test/reports/wiseflow_report_20241223_bigbrother666/README.md)をご参照ください。

また、テストスクリプトもオープンソース化しましたので、より多くのテスト結果の提出をお待ちしています。wiseflowはオープンソースプロジェクトであり、皆様の共同貢献を通じて「誰もが使える情報収集ツール」を作り上げたいと考えています！

詳細は[test/README_EN.md](./test/README_EN.md)をご参照ください。

現段階では、**テスト結果の提出はプロジェクトコードの提出と同等**とみなされ、contributorとして認められ、さらには商業化プロジェクトへの参加招待を受ける可能性もあります！

また、pocketbaseのダウンロードとユーザー名/パスワード設定方法を改善しました。@ourinesのinstall_pocketbase.shスクリプトの貢献に感謝いたします。

（dockerでの実行方案は一時的に削除されました。皆様にとってあまり便利ではないと感じたため...）

🌟 **V0.3.6バージョン予告**

V0.3.6バージョンは2024年12月30日までにリリース予定で、このバージョンはv0.3.5のパフォーマンス最適化版となります。情報抽出の品質が大幅に向上し、さらに視覚大規模モデルを導入して、ウェブページの情報が不足している場合にページ画像情報を補完として抽出します。

**V0.3.xプラン**

- WeChat公式アカウントのwxbotなしでの購読サポートを試行（V0.3.7）
- RSS情報ソースのサポートを導入（V0.3.8）
- LLM駆動の軽量知識グラフを導入し、ユーザーがinfosから洞察を得られるよう支援（V0.3.9）

V0.3.5バージョンからwiseflowは全く新しいアーキテクチャを採用し、[Crawlee](https://github.com/apify/crawlee-python)を基本クローラーとタスク管理フレームワークとして導入し、ページ取得能力を大幅に向上させました。今後もwiseflowのページ取得能力を継続的に向上させていきます。うまく取得できないページがありましたら、[issue #136](https://github.com/TeamWiseFlow/wiseflow/issues/136)でフィードバックをお願いします。

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

**Windowsユーザーは事前にGit Bashツールをダウンロードしてください** [リンク](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. ルートディレクトリのinstall_pocketbase.shスクリプトを実行

このスクリプトは、pocketbase（バージョン0.23.4）のダウンロードと設定をガイドし、coreディレクトリの下に.envファイルを作成します。

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

Wiseflow 0.3.xはデータベースとしてpocketbaseを使用しています。pocketbaseクライアント（バージョン0.23.4をダウンロードして[pb](./pb)ディレクトリに配置することを忘れないでください）を手動でダウンロードし、スーパーユーザーを手動で作成することもできます（.envファイルに保存することを忘れないでください）。

詳細については、[pb/README.md](/pb/README.md)を参照してください。

### 3. core/.envファイルの設定を続行

🌟 **これは以前のバージョンとは異なります** - V0.3.5以降、.envファイルは[core](./core)フォルダに配置する必要があります。

#### 3.1 大規模言語モデルの設定

Wiseflowは LLMネイティブアプリケーションですので、プログラムに安定したLLMサービスを提供するようにしてください。

🌟 **Wiseflowはモデルサービスのソースを制限しません - サービスがopenAI SDKと互換性があれば、ollama、Xinferenceなどのローカルにデプロイされたサービスを含め、すべて使用可能です**

#### 推奨1：Siliconflowが提供するMaaSサービスを使用

Siliconflowは、主流のオープンソースモデルのほとんどにオンラインMaaSサービスを提供しています。蓄積された推論加速技術により、そのサービスは速度と価格の両面で大きな利点があります。siliconflowのサービスを使用する場合、.envの設定は以下を参考にしてください：

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://api.siliconflow.cn/v1"
export PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
export SECONDARY_MODEL="Qwen/Qwen2.5-7B-Instruct"
export VL_MODEL="OpenGVLab/InternVL2-26B"
```
      
😄 よろしければ、私の[siliconflow紹介リンク](https://cloud.siliconflow.cn?referrer=clx6wrtca00045766ahvexw92)をご利用ください。これにより、私もより多くのトークン報酬を獲得できます 🌹

#### 推奨2：OpenAI、Claude、Geminiなどのクローズドソース商用モデルにはAiHubMixプロキシを使用

情報ソースが主に非中国語のページで、抽出された情報が中国語である必要がない場合は、OpenAI、Claude、Geminiなどのクローズドソース商用モデルの使用をお勧めします。サードパーティプロキシの**AiHubMix**を試すことができます。OpenAI、Claude、Google、Llamaなど、主要なAIモデルに1つのAPIで簡単にアクセスできます。

AiHubMixモデルを使用する場合、.envの設定は以下を参考にしてください：

```bash
export LLM_API_KEY=Your_API_KEY
export LLM_API_BASE="https://aihubmix.com/v1" # referhttps://doc.aihubmix.com/
export PRIMARY_MODEL="gpt-4o"
export SECONDARY_MODEL="gpt-4o-mini"
export VL_MODEL="gpt-4o"
```
😄 [AiHubMixの紹介リンク](https://aihubmix.com?aff=Gp54)からご登録いただけますと幸いです 🌹

#### ローカル大規模言語モデルサービスのデプロイ

Xinferenceを例にすると、.envの設定は以下を参考にできます：

```bash
# LLM_API_KEY='' no need for local service, please comment out or delete
export LLM_API_BASE='http://127.0.0.1:9997'
export PRIMARY_MODEL=launched_model_id
export SECONDARY_MODEL=launched_model_id
export VL_MODEL=launched_model_id
```

#### 3.2 Pocketbaseのアカウントとパスワードの設定

```bash
export PB_API_AUTH="test@example.com|1234567890" 
```

これはpocketbaseデータベースのスーパーユーザー名とパスワードを設定する場所です。|で区切ることを忘れないでください（install_pocketbase.shスクリプトが正常に実行された場合、これは既に存在しているはずです）

#### 3.3 その他のオプション設定

以下はすべてオプションの設定です：
- #VERBOSE="true" 

  観察モードを有効にするかどうか。有効にすると、デバッグ情報がloggerファイルに記録されます（デフォルトではコンソールにのみ出力）。

- #PROJECT_DIR="work_dir" 

    プロジェクトの実行時データディレクトリ。設定しない場合、デフォルトで`core/work_dir`になります。注意：現在、core全体のディレクトリがコンテナにマウントされているため、直接アクセスできます。

- #PB_API_BASE="" 

  pocketbaseがデフォルトのIPまたはポートで実行されていない場合にのみ設定が必要です。デフォルトの状況では、これを無視できます。

### 4. プログラムの実行

✋ V0.3.5バージョンのアーキテクチャと依存関係は以前のバージョンと大きく異なります。必ずコードを再取得し、pb_dataを削除（または再構築）してください。

condaを使用して仮想環境を構築することをお勧めします（もちろん、このステップをスキップするか、他のPython仮想環境ソリューションを使用することもできます）

```bash
conda create -n wiseflow python=3.10
conda activate wiseflow
```

その後

```bash
cd wiseflow
cd core
pip install -r requirements.txt
chmod +x run.sh
./run_task.sh # if you just want to scan sites one-time (no loop), use ./run.sh
```

🌟 このスクリプトは、pocketbaseが既に実行されているかどうかを自動的に判断します。実行されていない場合は自動的に起動します。ただし、ctrl+cまたはctrl+zでプロセスを終了した場合、ターミナルを閉じるまでpocketbaseプロセスは終了しないことに注意してください。

run_task.shは定期的にクローリング・抽出タスクを実行します（起動時に即座に実行され、その後1時間ごとに実行されます）。1回だけ実行する必要がある場合は、run.shスクリプトを使用できます。


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

商用およびカスタムコラボレーションについては、**Email：zm.zhao@foxmail.com** までお問い合わせください

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