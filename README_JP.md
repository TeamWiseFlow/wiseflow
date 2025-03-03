# AIチーフインテリジェンスオフィサー（Wiseflow）

**[English](README_EN.md) | [简体中文](README.md) | [한국어](README_KR.md)**

🚀 **AIチーフインテリジェンスオフィサー**（Wiseflow）は、大規模言語モデルの思考・分析能力を活用して、様々な情報源から特定の情報を正確に抽出できる俊敏な情報マイニングツールです。プロセス全体で人間の介入を必要としません。

**私たちが欠けているのは情報ではなく、大量の情報からノイズをフィルタリングし、価値ある情報を明らかにすることです**

🌱首席情報官がどのようにあなたの時間を節約し、無関係な情報をフィルタリングし、関心のあるポイントを整理するのかを見てみましょう！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

🌟 注意：最近、多くの人が DeepSeek R1 を代表とする reasoning モデルを絶賛しているのを耳にするかもしれません（私もそれを否定するわけではありません）。しかし、WiseFlow における情報抽出や要約タスクには複雑な論理推論は必要なく、むしろ reasoning モデルを使用すると処理時間とコストが大幅に増加してしまいます！この結論について詳しく知りたい方は、以下のテストレポートを参照してください：[wiseflow V0.38 with deepseek series report](./test/reports/wiseflow_report_v038_dp_bigbrother666/README.md)。

現在、通常の大規模言語モデルの使用を引き続き推奨しています。また、従来のプロンプトを改良し、7B および 14B モデルの出力品質を向上させました。生成速度やコストを重視する場合、`PRIMARY_MODEL` と `SECONDARY_MODEL` の両方を `Qwen2.5-14B-Instruct` に設定することを推奨します。


## 🔥 V0.3.9 リリース

v0.3.9 は v0.3.8 のアップグレード修復バージョンで、crawl4ai 0.4.248 に適応し、パフォーマンスを最適化し、累積されたバグを修正し、0.3.xシリーズの長期安定バージョンでもあります。

詳細については、[CHANGELOG.md](./CHANGELOG.md)をご参照ください。

**V0.3.7 およびそれ以前のバージョンのユーザーは、pb フォルダー内で ./pocketbase migrate を実行してください**

以下のコミュニティメンバーに、V0.3.5～V0.3.9バージョンでのPRに感謝します：

  - @ourines install_pocketbase.sh自動インストールスクリプトの提供
  - @ibaoger Windows用pocketbase自動インストールスクリプトの提供
  - @tusik 非同期llm wrapperの提供とAsyncWebCrawlerのライフサイクル問題の発見
  - @c469591 Windows版起動スクリプトの提供
  - @braumye がDocker実行案を貢献しました
  - @YikaJ が install_pocketbase.sh の最適化を提供しました

**wiseflow の次のオープンソースバージョンは、少なくとも2ヶ月の待機が必要となる見込みです。全く新しい0.4.xアーキテクチャを開始します。**

0.4.xに関しては、具体的な製品ロードマップについてずっと考えてきましたが、現時点では、より多くの実際のユーザーからのフィードバックが必要です。[issue](https://github.com/TeamWiseFlow/wiseflow/issues) にて、皆様からの利用ニーズをより多くご提案いただければ幸いです。
  
### 🌟 テストレポート

最新の抽出戦略では、7bクラスのモデルでもリンク分析と抽出タスクを適切に実行できることがわかりました。テスト結果は[report](./test/reports/wiseflow_report_v037_bigbrother666/README.md)をご参照ください。

ただし、情報要約タスクについては、引き続き32b以上のモデルの使用を推奨します。具体的な推奨事項は最新の[env_sample](./env_sample)をご参照ください。

引き続き、より多くのテスト結果の提出を歓迎し、様々な情報源でのwiseflowの最適な使用方法を共に探求していきましょう。

現段階では、**テスト結果の提出はプロジェクトコードの提出と同等**とみなされ、contributorとして受け入れられ、商業化プロジェクトへの参加招待も受けられます！詳細は[test/README.md](./test/README.md)をご参照ください。


## ✋ wiseflow と従来のクローラーツール、AI検索、知識ベース（RAG）プロジェクトの違いは何ですか？

wiseflowは2024年6月末にV0.3.0バージョンをリリースして以来、オープンソースコミュニティから広く注目を集めており、さらに多くのメディアが自発的に報道してくれました。ここでまず感謝の意を表します！

しかし、私たちは一部の関心者がwiseflowの機能ポジションについていくつかの理解のズレを持っていることに気づきました。以下の表は、従来のクローラーツール、AI検索、知識ベース（RAG）類プロジェクトとの比較を通じて、wiseflowの最新の製品ポジションについての私たちの考えを表しています。

|          | **首席情報官（Wiseflow）** との比較説明| 
|-------------|-----------------|
| **クローラーツール** | まず、wiseflowはクローラーツールを基にしたプロジェクトですが、従来のクローラーツールは情報抽出において明確なXpathなどの情報を手動で提供する必要があります...これは一般ユーザーを阻むだけでなく、汎用性もありません。異なるウェブサイト（既存のウェブサイトのアップグレード後を含む）に対して、手動で再分析し、プログラムを更新する必要があります。wiseflowはLLMを使用してウェブページの分析と抽出を自動化することに努めており、ユーザーはプログラムに自分の関心点を伝えるだけで済みます。Crawl4aiを例として比較すると、Crawl4aiはLLMを使用して情報抽出を行うクローラーであり、wiseflowはクローラーツールを使用するLLM情報抽出ツールです。 |
| **AI検索（各種「ディープサーチ」を含む）** | AI検索の主な応用シナリオは**特定の問題に対する即時回答**です。例：「XX社の創設者は誰ですか」、「xxブランドのxx製品はどこで販売されていますか」。ユーザーが求めているのは**一つの答え**です。一方、wiseflowの主な応用シナリオは**ある方面の情報を持続的に収集する**ことです。例えば、XX社の関連情報の追跡、XXブランドの市場行動の継続的な追跡……これらのシナリオでは、ユーザーは関心事（ある会社、あるブランド）、さらには情報源（サイトURLなど）を提供できますが、具体的な検索問題を提起することはできません。ユーザーが求めているのは**一連の関連情報**です|
| **知識ベース（RAG）類プロジェクト** | 知識ベース（RAG）類プロジェクトは通常、既存の情報に基づく下流タスクであり、一般的にプライベート知識（例えば、企業内の操作マニュアル、製品マニュアル、政府部門の文書など）を対象としています；wiseflowは現在、下流タスクを統合しておらず、インターネット上の公開情報を対象としています。「エージェント」の観点から見ると、両者は異なる目的のために構築されたエージェントであり、RAG類プロジェクトは「（内部）知識アシスタントエージェント」であり、wiseflowは「（外部）情報収集エージェント」です|


## 📥 インストールと使用

### 1. コードリポジトリのクローン

🌹 いいね、forkは良い習慣です 🌹

**Windowsユーザーは事前にGit Bashツールをダウンロードしてください** [リンク](https://git-scm.com/downloads/win)

```bash
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

### 2. ルートディレクトリのinstall_pocketbase スクリプトを実行

linux/macosユーザーは以下を実行してください

```bash
chmod +x install_pocketbase
./install_pocketbase
```

**Windowsユーザーは[install_pocketbase.ps1](./install_pocketbase.ps1)スクリプトを実行してください**

Wiseflow 0.3.xはデータベースとしてpocketbaseを使用しています。pocketbaseクライアント（バージョン0.23.4をダウンロードして[pb](./pb)ディレクトリに配置することを忘れないでください）を手動でダウンロードし、スーパーユーザーを手動で作成することもできます（.envファイルに保存することを忘れないでください）。

詳細については、[pb/README.md](/pb/README.md)を参照してください。

### 3. core/.envファイルの設定を続行

🌟 **これは以前のバージョンとは異なります** - V0.3.5以降、.envファイルは[core](./core)フォルダに配置する必要があります。

#### 3.1 大規模言語モデルの設定

Wiseflowは LLMネイティブアプリケーションですので、プログラムに安定したLLMサービスを提供するようにしてください。

🌟 **Wiseflowはモデルサービスのソースを制限しません - サービスがopenAI SDKと互換性があれば、ollama、Xinferenceなどのローカルにデプロイされたサービスを含め、すべて使用可能です**

#### 推奨1：Siliconflowが提供するMaaSサービスを使用

Siliconflowは、主流のオープンソースモデルのほとんどにオンラインMaaSサービスを提供しています。蓄積された推論加速技術により、そのサービスは速度と価格の両面で大きな利点があります。siliconflowのサービスを使用する場合、.envの設定は以下を参考にしてください：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1"
PRIMARY_MODEL="Qwen/Qwen2.5-32B-Instruct"
SECONDARY_MODEL="Qwen/Qwen2.5-14B-Instruct"
VL_MODEL="deepseek-ai/deepseek-vl2"
```
      
😄 よろしければ、私の[siliconflow紹介リンク](https://cloud.siliconflow.cn/i/WNLYbBpi) をご利用ください。これにより、私もより多くのトークン報酬を獲得できます 🌹

#### 推奨2：OpenAI、Claude、Geminiなどのクローズドソース商用モデルにはAiHubMixプロキシを使用

情報ソースが主に非中国語のページで、抽出された情報が中国語である必要がない場合は、OpenAI、Claude、Geminiなどのクローズドソース商用モデルの使用をお勧めします。サードパーティプロキシの**AiHubMix**を試すことができます。OpenAI、Claude、Google、Llamaなど、主要なAIモデルに1つのAPIで簡単にアクセスできます。

AiHubMixモデルを使用する場合、.envの設定は以下を参考にしてください：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # referhttps://doc.aihubmix.com/
PRIMARY_MODEL="gpt-4o"
SECONDARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
```
😄 [AiHubMixの紹介リンク](https://aihubmix.com?aff=Gp54)からご登録いただけますと幸いです 🌹

#### ローカル大規模言語モデルサービスのデプロイ

Xinferenceを例にすると、.envの設定は以下を参考にできます：

```
# LLM_API_KEY='' no need for local service, please comment out or delete
LLM_API_BASE='http://127.0.0.1:9997'
PRIMARY_MODEL=launched_model_id
VL_MODEL=launched_model_id
```

#### 3.2 Pocketbaseのアカウントとパスワードの設定

```
PB_API_AUTH="test@example.com|1234567890" 
```

これはpocketbaseデータベースのスーパーユーザー名とパスワードを設定する場所です。|で区切ることを忘れないでください（install_pocketbase.shスクリプトが正常に実行された場合、これは既に存在しているはずです）

#### 3.3 智谱（bigmodel）プラットフォームキーの設定（検索エンジンサービスに使用）

```
ZHIPU_API_KEY=Your_API_KEY
```

（申請先：https://bigmodel.cn/ 現在無料）

#### 3.4 その他のオプション設定

以下はすべてオプションの設定です：
- #VERBOSE="true" 

  観察モードを有効にするかどうか。有効にすると、デバッグ情報がloggerファイルに記録されます（デフォルトではコンソールにのみ出力）。

- #PROJECT_DIR="work_dir" 

    プロジェクトの実行時データディレクトリ。設定しない場合、デフォルトで`core/work_dir`になります。注意：現在、core全体のディレクトリがコンテナにマウントされているため、直接アクセスできます。

- #PB_API_BASE="" 

  pocketbaseがデフォルトのIPまたはポートで実行されていない場合にのみ設定が必要です。デフォルトの状況では、これを無視できます。

- #LLM_CONCURRENT_NUMBER=8 

  llm の同時リクエスト数を制御するために使用されます。デフォルトは1です（llm provider が設定された同時性をサポートしていることを確認してください。ローカル大規模モデルはハードウェアベースに自分がない限り慎重に使用してください）

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
```

その後、MacOS&Linuxユーザーは実行します

```bash
chmod +x run.sh
./run.sh
```

Windowsユーザーは実行します

```bash
python windows_run.py
```

- このスクリプトはpocketbaseが既に実行されているかどうかを自動的に判断し、実行されていない場合は自動で起動します。ただし、注意してください、ctrl+cまたはctrl+zでプロセスを終了させた場合、pocketbaseプロセスは終了しないため、terminalを閉じるまでです。

- run.shはまず、activatedがtrueに設定されたすべての信源に対して一度のクロールタスクを実行し、その後、設定された頻率で時間単位で周期的に実行します。

### 5. フォーカスポイントと情報源の追加
    
プログラムを起動した後、pocketbase Admin dashboard UI (http://127.0.0.1:8090/_/) を開いてください。

#### 5.1 サイトフォームを開く

このフォームを使用して情報源を構成できます。注意：情報源は次のステップの focus_point フォームで選択する必要があります。

サイトフィールドの説明：
- url, 情報源のurl。情報源には具体的な記事ページを指定する必要はありません。記事リストページを指定してください。
- type, タイプ。web または rss。
    
#### 5.2 フォーカスポイントフォームを開く

このフォームを使用してあなたのフォーカスポイントを指定できます。LLMはこれに基づいて情報を抽出、フィルタリング、分類します。
    
フィールドの説明：
- focuspoint, フォーカスポイントの説明（必須）。例：”新年セールの割引“、”入札通知“
- explanation，フォーカスポイントの詳細な説明または具体的な約束。例：”xxシリーズの製品”、”2025年1月1日以降に発行され、100万円以上の“
- activated, アクティブ化するかどうか。オフにすると、そのフォーカスポイントは無視されます。オフにした後、再度オンにできます。
- per_hour, クロール頻度。単位は時間で、整数型（1~24の範囲）。クロール頻度を1日1回を超えないように設定することをお勧めします。つまり、24に設定します。
- search_engine, クロール時に検索エンジンをオンにするかどうか
- sites，対応する情報源を選択

**注意：V0.3.8以降、設定の調整はプログラムを再起動する必要はありません。次回の実行時に自動的に適用されます。**

## 🐳 Docker デプロイメント

Docker を使用して Wiseflow をデプロイしたい場合、完全なコンテナ化サポートを提供しています。

### 1. 前提条件

システムに Docker がインストールされていることを確認してください。

### 2. 環境変数の設定

ルートディレクトリで`env_docker`ファイルを`.env`としてコピーします：

```bash
cp env_docker .env
```

### 3. 《[インストールと使用方法](#-インストールと使用)》セクションに従って`.env`ファイルを修正

以下の環境変数は必要に応じて修正する必要があります：

```bash
LLM_API_KEY=""
LLM_API_BASE="https://api.siliconflow.cn/v1"
PB_SUPERUSER_EMAIL="test@example.com"
PB_SUPERUSER_PASSWORD="1234567890" #no '&' in the password and at least 10 characters
```

### 4. サービスの開始

プロジェクトのルートディレクトリで実行：

```bash
docker compose up -d
```

サービス開始後：

- PocketBase 管理インターフェース：http://localhost:8090/_/
- Wiseflow サービスが自動的に実行され、PocketBase に接続されます

### 5. サービスの停止

```bash
docker compose down
```

### 6. 重要な注意事項

- `./pb/pb_data`ディレクトリは PocketBase 関連ファイルの保存に使用されます
- `./docker/pip_cache`ディレクトリは Python 依存パッケージのキャッシュを保存し、再ダウンロードを避けるために使用されます
- `./core/work_dir`ディレクトリは Wiseflow のランタイムログの保存に使用されます。`.env`ファイルで`PROJECT_DIR`を修正できます

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

- crawl4ai（Open-source LLM Friendly Web Crawler & Scraper） https://github.com/unclecode/crawl4ai
- pocketbase (Open Source realtime backend in 1 file) https://github.com/pocketbase/pocketbase
- python-pocketbase (pocketBase client SDK for python) https://github.com/vaphes/pocketbase
- feedparser (Parse feeds in Python) https://github.com/kurtmckee/feedparser

また、[GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler)、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct)  からもインスピレーションを受けています。

## Citation

もしあなたが関連する作業で本プロジェクトの一部または全部を参照または引用した場合、以下の情報を記載してください：

```
Author：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Licensed under Apache2.0
```
