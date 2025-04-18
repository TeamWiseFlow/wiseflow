# AIチーフインテリジェンスオフィサー（Wiseflow）

**[English](README_EN.md) | [简体中文](README.md) | [한국어](README_KR.md)**

🚀 **大規模言語モデルを活用し、日々、膨大な情報や様々な情報源から、あなたが本当に興味のある情報を抽出します！**

私たちが欠けているのは情報ではなく、大量の情報からノイズをフィルタリングし、価値ある情報を明らかにすることです

🌱首席情報官がどのようにあなたの時間を節約し、無関係な情報をフィルタリングし、関心のあるポイントを整理するのかを見てみましょう！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 おめでとうございます、また無料で首席情報官を使用できる時が来ました！

2025年4月14日、智譜は新しいZ1シリーズモデルとGLM-4-0414シリーズモデルをリリースし、対応する32Bと9Bのオープンソースバージョンを公開しました。同日遅く、シリコンフローはこれらのオープンソースモデルのオンラインサービスを開始しました。

私たちもこれらの新しくリリースされたモデルを最初にテストし、テスト結果は驚くほど良好でした。現在両プラットフォームで無料のglm-z1-flash/GLM-Z1-9B-0414とglm-4-flash-250414/GLM-4-9B-0414でも、wiseflowが扱う抽出と要約タスクを比較的理想的に完了できます。

詳細なテストレポートは[test/reports/wiseflow_report_v038_dp_bigbrother666/GLM_report_0416.md](./test/reports/wiseflow_report_v038_dp_bigbrother666/GLM_report_0416.md)をご覧ください。

上記のモデルに切り替えたい場合は、.envファイルのLLM_API_KEY、LLM_API_BASE、PRIMARY_MODEL、SECONDARY_MODEL設定を変更するだけで済みます。（不慣れな方は以下の説明をご覧ください）

また、9bモデルのサイズを考慮すると、ローカルデプロイも適しています。

同時に、現在使用中の智譜検索ソリューションが英語検索をサポートしていない問題に対処するため、Jina検索ソリューションに切り替えました。価格が低く、https://jina.ai/ にログインするだけでAPIを取得できます（登録不要、個人使用には十分な量と同時実行性が提供されます）。

### 設定をしたくない方も、**AI首席情報官**オンラインサービスをご利用いただけます。デプロイや設定は不要で、各種キーの申請も不要、登録するだけで使用できます！

オンライン体験アドレス：https://www.aiqingbaoguan.com/ 

現在、登録すると15ポイントの計算能力値がプレゼントされます（各注目ポイントは毎日1ポイント消費、情報源の数は問いません）。

*オンラインサーバーは阿里云に構築されています。中国大陸以外のサイトへのアクセスは制限されています。また、オンラインサービスは現在、WeChat公式アカウントをサポートしていません。もし、あなたの情報源がこれらのタイプであれば、開源版を自分でデプロイすることをお勧めします。*


## 🌟 過去2週間のコントリビューター

  - @zhudongwork PR #354
  - @cdxiaodong PR #357


## 🧐 'deep search' VS 'wide search'

Wiseflowの製品ポジショニングは「wide search（広域検索）」と呼んでいます。これは現在注目されている「deep search（深層検索）」とは対照的なものです。

具体的に言うと、「deep search」は特定の質問に対してLLMが自律的かつ動的に検索パスを計画し、様々なページを継続的に探索し、十分な情報を収集して回答やレポートを作成します。しかし、時には特定の問題がなく、深い探索も必要なく、幅広い情報収集（例えば、業界情報収集、対象の背景情報収集、顧客情報収集など）だけが必要な場合があります。この場合、広さが明らかに重要になります。「deep search」でもこのタスクを実現できますが、それは大砲で蚊を撃つようなもので、非効率でコストも高くなります。Wiseflowは、まさにこの「wide search」シナリオのために作られた強力なツールです。

## ✋ What makes wiseflow different from other ai-powered crawlers?

他のAIを活用したクローラーとの最大の違いは、スクレイパーの段階で、既存のクローラーとは異なるパイプライン、つまり「クロールとチェックの統合」戦略を提案していることです。具体的には、従来のフィルター抽出プロセス（もちろん、このプロセスもCrawl4aiのようにLLMを組み込むことができます）を放棄し、単一のページを最小処理単位として扱いません。Crawl4aiのhtml2markdownをベースに、さらにページをブロックに分割し、一連の特徴アルゴリズムに基づいて、「本文ブロック」と「外部リンクブロック」に分類します。分類に応じて異なるLLM抽出戦略を使用します（各ブロックはLLMによって一度だけ分析されますが、分析戦略は異なり、トークンの無駄を避けます）。このアプローチは、リストページ、コンテンツページ、および混合ページに対応できます。

  - 「本文ブロック」については、関心のあるポイントに従って直接要約を抽出し、情報が分散するのを防ぎ、さらにはこのプロセスで翻訳などを直接完了させます。
  - 「外部リンクブロック」については、ページのレイアウトなどの情報を考慮して、どのリンクをさらに探索する価値があり、どれを無視できるかを判断します。したがって、ユーザーは手動で深さや最大クロール数を設定する必要はありません。

このアプローチは、実際にはAI検索と非常によく似ています。

さらに、特定の種類のページ（WeChat公式アカウントの記事など、驚くべきことに9つの形式があります...）のために特別に設計された解析モジュールも作成しました。この種のコンテンツについては、Wiseflowは現在、同種の製品の中で最高の解析結果を提供しています。

## ✋ What's Next (4.x plan)?

### Crawler fetching 段階の強化

3.x アーキテクチャでは、クローラーのフェッチ部分は完全に Crawl4ai を使用しています。4.x では、通常のページの取得には引き続きこのスキームを使用しますが、ソーシャルプラットフォームのフェッチングスキームを徐々に追加していきます。

### Insight モジュール

実際、本当に価値があるのは「取得できる情報」ではなく、これらの情報の下に隠された「暗黙の情報」である可能性があります。取得された情報をインテリジェントに関連付け、その下に隠された「暗黙の情報」を分析および抽出できることが、4.x で重点的に構築する Insight モジュールです。


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

Wiseflow 3.xはデータベースとしてpocketbaseを使用しています。pocketbaseクライアント（バージョン0.23.4をダウンロードして[pb](./pb)ディレクトリに配置することを忘れないでください）を手動でダウンロードし、スーパーユーザーを手動で作成することもできます（.envファイルに保存することを忘れないでください）。

詳細については、[pb/README.md](/pb/README.md)を参照してください。

### 3. core/.envファイルの設定を続行

🌟 **これは以前のバージョンとは異なります** - V3.5以降、.envファイルは[core](./core)フォルダに配置する必要があります。

#### 3.1 大規模言語モデルの設定

Wiseflowは LLMネイティブアプリケーションですので、プログラムに安定したLLMサービスを提供するようにしてください。

🌟 **Wiseflowはモデルサービスのソースを制限しません - サービスがopenAI SDKと互換性があれば、ollama、Xinferenceなどのローカルにデプロイされたサービスを含め、すべて使用可能です**

#### 推奨1：Siliconflowが提供するMaaSサービスを使用

Siliconflowは、主流のオープンソースモデルのほとんどにオンラインMaaSサービスを提供しています。蓄積された推論加速技術により、そのサービスは速度と価格の両面で大きな利点があります。siliconflowのサービスを使用する場合、.envの設定は以下を参考にしてください：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1" # bigmodels https://open.bigmodel.cn/api/paas/v4/ 
PRIMARY_MODEL="THUDM/GLM-4-9B-0414"  # for better performance THUDM/GLM-4-32B-0414
# bigmodel glm-z1-flash / better performance: glm-4-air-250414
SECONDARY_MODEL="THUDM/GLM-Z1-9B-0414" # for better performance THUDM/GLM-Z1-32B-0414
# bigmodel glm-4-flash-250414
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
# bigmodel glm-4v-flash (free now)
PROJECT_DIR="work_dir"
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
PROJECT_DIR="work_dir"
```
😄 [AiHubMixの紹介リンク](https://aihubmix.com?aff=Gp54)からご登録いただけますと幸いです 🌹

#### ローカル大規模言語モデルサービスのデプロイ

Xinferenceを例にすると、.envの設定は以下を参考にできます：

```
# LLM_API_KEY='' no need for local service, please comment out or delete
LLM_API_BASE='http://127.0.0.1:9997' # 'http://127.0.0.1:11434/v1' for ollama
PRIMARY_MODEL=launched_model_id
VL_MODEL=launched_model_id
PROJECT_DIR="work_dir"
```

#### 3.2 Pocketbaseのアカウントとパスワードの設定

```
PB_API_AUTH="test@example.com|1234567890" 
```

これはpocketbaseデータベースのスーパーユーザー名とパスワードを設定する場所です。|で区切ることを忘れないでください（install_pocketbase.shスクリプトが正常に実行された場合、これは既に存在しているはずです）

#### 3.3 JINA_API_KEY 設定（検索エンジンサービスに使用）

https://jina.ai/ から取得できます。現在、登録する必要はありませんが、高並行や商用の需要がある場合は、充電後に使用してください。

```
JINA_API_KEY=Your_API_KEY
```

#### 3.4 その他のオプション設定

以下はすべてオプションの設定です：
- #VERBOSE="true" 

  観察モードを有効にするかどうか。有効にすると、デバッグ情報がloggerファイルに記録されます（デフォルトではコンソールにのみ出力）。

- #PB_API_BASE="" 

  pocketbaseがデフォルトのIPまたはポートで実行されていない場合にのみ設定が必要です。デフォルトの状況では、これを無視できます。

- #LLM_CONCURRENT_NUMBER=8 

  llm の同時リクエスト数を制御するために使用されます。デフォルトは1です（llm provider が設定された同時性をサポートしていることを確認してください。ローカル大規模モデルはハードウェアベースに自分がない限り慎重に使用してください）

### 4. プログラムの実行

condaを使用して仮想環境を構築することをお勧めします（もちろん、このステップをスキップするか、他のPython仮想環境ソリューションを使用することもできます）

```bash
conda create -n wiseflow python=3.12
conda activate wiseflow
```

その後

```bash
cd wiseflow
cd core
pip install -r requirements.txt
python -m playwright install --with-deps chromium
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
- focuspoint, フォーカスポイントの説明（必須）。例："新年セールの割引"、"入札通知"
- explanation，フォーカスポイントの詳細な説明または具体的な約束。例："xxシリーズの製品"、"2025年1月1日以降に発行され、100万円以上の"
- activated, アクティブ化するかどうか。オフにすると、そのフォーカスポイントは無視されます。オフにした後、再度オンにできます。
- per_hour, クロール頻度。単位は時間で、整数型（1~24の範囲）。クロール頻度を1日1回を超えないように設定することをお勧めします。つまり、24に設定します。
- search_engine, クロール時に検索エンジンをオンにするかどうか
- sites，対応する情報源を選択

**注意：V3.8以降、設定の調整はプログラムを再起動する必要はありません。次回の実行時に自動的に適用されます。**

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
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.cn/v1" # bigmodels https://open.bigmodel.cn/api/paas/v4/ 
PRIMARY_MODEL="THUDM/GLM-4-9B-0414"  # for better performance THUDM/GLM-4-32B-0414
# bigmodel glm-z1-flash / better performance: glm-4-air-250414
SECONDARY_MODEL="THUDM/GLM-Z1-9B-0414" # for better performance THUDM/GLM-Z1-32B-0414
# bigmodel glm-4-flash-250414
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
# bigmodel glm-4v-flash (free now)
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

3、オンラインサービスも間もなくsync APIをリリース予定です。オンラインでのクロール結果をローカルに同期し、「動的知識ベース」などの構築に活用できます。ご期待ください：

  - オンライン体験アドレス：https://www.aiqingbaoguan.com/
  - オンラインサービス API 利用事例：https://github.com/TeamWiseFlow/wiseflow_plus

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
