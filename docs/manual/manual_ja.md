# WiseFlow インストールとユーザーマニュアル

**3.xユーザーは元のコードリポジトリとpbフォルダを完全に削除し、4.xコードリポジトリを再クローンする必要があります。そうしないと正常に起動できません。**

**4.0ユーザーがバージョン4.1にアップグレードする場合、最新のコードをプルした後、まず ./pb/pocketbase migrate コマンドを実行する必要があります。そうしないと正常に起動できません。**

## 📋 システム要件

- **Python**: 3.10 - 3.12（3.12推奨）
- **オペレーティングシステム**: macOS、Linux、またはWindows
- **ハードウェア要件**: 8GB以上のRAM（オンラインLLMサービス使用時）

## 📥 使用方法

WiseFlow 4.xのユーザーインターフェースはPocketBaseを使用しています（理想的ではありませんが、現在の最適なソリューションです）

### 1. インターフェースへのアクセス

🌐 起動成功後、ブラウザを開いて以下にアクセスしてください：**http://127.0.0.1:8090/_/**

### 2. 情報源とフォーカスポイントの設定

focus_pointフォームに切り替えてください

このフォームを通じて、フォーカスポイントを指定できます。LLMはこれに基づいて情報を精緻化、フィルタリング、分類します。

フィールドの説明：
- focuspoint（必須）：フォーカスポイントの説明。LLMにどのような情報が必要かを伝えます。例：「上海の小中一貫校情報」や「入札通知」など
- restrictions（オプション）：フォーカスポイントのフィルタリング制約。LLMにどの情報を除外すべきかを伝えます。例：「上海市公式発表の中学校入学情報のみ」や「2025年1月1日以降に発表され、金額が100万以上のもの」など
- explanation（オプション）：特殊な概念や専門用語の説明。LLMの誤解を避けるため。例：「小中一貫校とは小学校から中学校への移行を指す」
- activated：有効化するかどうか。オフにするとこのフォーカスポイントは無視され、後で再度オンにできます
- freq：クロール頻度（時間単位）、整数型（1日1回を超えないことを推奨、つまり24に設定、最小値は2、つまり2時間ごとにクロール）
- search：詳細な検索ソースを設定します。現在、bing、github、arxiv、ebay をサポートしています
- sources：対応する情報源を選択

#### 💡 フォーカスポイントの書き方は非常に重要であり、情報抽出が要件を満たすかどうかを直接決定します。具体的には：

  - ユースケースが業界情報、学術情報、政策情報などの追跡であり、情報源に広範な検索が含まれている場合、フォーカスポイントは検索エンジンに似たキーワードモデルを使用する必要があります。同時に、制約と説明を追加し、必要に応じて役割と目的を定義する必要があります。

  - ユースケースが競合他社の追跡、身元調査などであり、情報源が競合他社のホームページ、公式アカウントなど非常に具体的な場合は、「値下げ情報」、「新製品情報」など、関心のある視点をフォーカスポイントとして入力するだけで済みます。

**フォーカスポイントの設定変更は、プログラムの再起動を必要とせず、次回の実行時に自動的に有効になります。**

情報源はsourcesページまたはfocus_pointsバインディングページのいずれかで追加できます。情報源追加フィールドの説明：

- type：タイプ、現在サポート：web、rss、wb（微博）、ks（快手）、mp（微信公式アカウント（4.0では一時的にサポートされていません、4.1を待っています））
- creators：クロールするクリエイターID（複数は「,」で区切り）、ks、wb、mpでのみ有効。ksとmpは'homefeed'の入力に対応（システムプッシュコンテンツを毎回取得することを表す）。このフィールドは空にすることもでき、その場合は情報源は検索のみに使用されます

  *注意：IDはプラットフォームの対応するWebバージョンのホームページリンクを使用してください。例えば、微博のIDがhttps://m.weibo.cn/profile/2656274875の場合、IDは2656274875です*

- url：情報源に対応するリンク、rssとwebタイプでのみ有効

### 3. 結果の表示

- infosページ：最終的に抽出された有用な情報を保存
- crawled_dataページ：クロールされた元のデータを保存
- ks_cacheページ：快手のキャッシュデータを保存
- wb_cacheページ：微博のキャッシュデータを保存

## 🌟 デプロイメントインストール

**デプロイメントインストールは3ステップだけ！**

**Windowsユーザーは事前にGit Bashツールをダウンロードし、bashで以下のコマンドを実行してください [Bashダウンロードリンク](https://git-scm.com/downloads/win)**·

### 📋 プロジェクトのソースコードをダウンロードし、uvとpocketbaseをインストール

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

上記の操作でuvのインストールが完了します。

次に、[pocketbase docs](https://pocketbase.io/docs/)からお使いのシステムに対応するpocketbaseプログラムをダウンロードし、[.pb](./pb/)フォルダに配置してください。

install_pocketbase.sh（MacOS/Linux用）またはinstall_pocketbase.ps1（Windows用）を使用してインストールすることもできます。

### 📥 env_sampleに基づいて.envファイルを設定

wiseflowフォルダ（プロジェクトルートディレクトリ）で、env_sampleに基づいて.envファイルを作成し、関連する設定を入力してください。

バージョン4.xでは、ユーザーが.envでPocketBaseのアカウント認証情報を提供する必要はなく、PocketBaseのバージョンも制限されていません。また、Secondary Modelの設定も一時的に削除されています。したがって、実際には4つのパラメータだけで設定を完了できます：

- LLM_API_KEY="" # LLMサービスのキー（OpenAI形式のAPIを提供するモデルサービスプロバイダーであればどれでも可、ローカルでデプロイされたollamaを使用する場合は設定不要）
- LLM_API_BASE="https://api.siliconflow.com/v1" # LLMサービスインターフェースアドレス
- JINA_API_KEY="" # 検索エンジンサービスのキー（Jina推奨、個人使用でも登録なしで申請可能）
- PRIMARY_MODEL="Qwen3-14B" # Qwen3-14Bまたは同様の思考モデル推奨
- VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct" # 視覚モデル、オプションだが推奨。必要なページ画像の分析に使用（プログラムはコンテキストに基づいて分析が必要かどうかを判断し、すべての画像を抽出するわけではありません）、最低Qwen2.5-VL-7B-Instructで十分です

### 🚀 さあ始めましょう！

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

✨ **これだけです！** 起動スクリプトは自動的に以下のタスクを完了します：
- ✅ 環境設定の確認
- ✅ プロジェクト依存関係の同期
- ✅ 仮想環境のアクティベート
- ✅ PocketBaseデータベースの起動
- ✅ WiseFlowアプリケーションの実行

プログラムは最初にすべての有効化されたソース（activatedがtrueに設定されているもの）に対してクロールタスクを実行し、その後は設定された頻度で時間単位で定期的に実行します。

⚠️ **注意：** `Ctrl+C`でプロセスを終了する場合、PocketBaseプロセスは自動的に終了しない可能性があり、手動で閉じるかターミナルを再起動する必要があります。

### 📝 手動インストール（オプション）

各ステップを手動で制御したい場合は、以下の手順に従ってください：

#### 1. ルートディレクトリのinstall_pocketbaseスクリプトを実行

Linux/macOSユーザーは以下を実行してください：

```bash
chmod +x install_pocketbase.sh
./install_pocketbase.sh
```

**Windowsユーザーは以下を実行してください：**
```powershell
.\install_pocketbase.ps1
```

#### 2. 仮想環境の作成とアクティベート

```bash
uv venv
source .venv/bin/activate  # Linux/macOS
# Windowsの場合：
# .venv\Scripts\activate
```

##### 4.2 依存関係のインストール

```bash
uv sync
```

これにより、WiseFlowとそのすべての依存関係がインストールされ、依存関係のバージョンの一貫性が確保されます。uv syncはプロジェクトの依存関係宣言を読み取り、仮想環境を同期します。

次にブラウザの依存関係をインストールします：

```bash
python -m playwright install --with-deps chromium
```

最後に、メインサービスを起動します：

```bash
python core/run_task.py
# Windowsの場合：
# python core\run_task.py
```

PocketBaseユーザーインターフェースを使用する必要がある場合は、PocketBaseサービスを起動します：

```bash
cd wiseflow/pb
./pocketbase serve
```

またはWindowsの場合：

```powershell
cd wiseflow\pb
.\pocketbase.exe serve
```

### 🔧 環境変数の設定

クイックスタートまたは手動インストールのいずれの場合も、env_sampleに基づいて.envファイルを作成する必要があります：

#### 1. LLM関連の設定

WiseFlowはLLMネイティブアプリケーションです。プログラムに安定したLLMサービスを提供してください。

🌟 **WiseFlowはモデルサービスプロバイダーを制限しません。OpenAI SDKと互換性のあるサービスであれば、ローカルでデプロイされたollama、Xinference、その他のサービスも含めて使用できます**

##### 推奨1：SiliconFlowのMaaSサービスを使用

SiliconFlowは、ほとんどの主流オープンソースモデルのオンラインMaaSサービスを提供しています。彼らの加速推論技術により、サービスは速度と価格の両方で優位性があります。SiliconFlowのサービスを使用する場合、.envの設定は以下のようになります：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://api.siliconflow.com/v1"
PRIMARY_MODEL="Qwen3-14B"
VL_MODEL="Pro/Qwen/Qwen2.5-VL-7B-Instruct"
CONCURRENT_NUMBER=8
```

😄 よろしければ、私の[SiliconFlow招待リンク](https://cloud.siliconflow.com/i/WNLYbBpi)を使用してください。そうすれば、より多くのトークン報酬を得ることができます 🌹

##### 推奨2：AiHubMixのプロキシされた海外のクローズドソース商用モデルサービス（OpenAI、Claude、Geminiなど）を使用

情報源が主に非中国語のページで、抽出された情報が中国語である必要がない場合は、OpenAI、Claude、Geminiなどの海外のクローズドソース商用モデルがより推奨されます。中国のネットワーク環境での直接接続、便利なAlipay支払い、アカウントブロックリスクの排除をサポートするサードパーティプロキシ**AiHubMix**を試すことができます。
AiHubMixのモデルを使用する場合、.envの設定は以下のようになります：

```
LLM_API_KEY=Your_API_KEY
LLM_API_BASE="https://aihubmix.com/v1" # 詳細は https://doc.aihubmix.com/ を参照
PRIMARY_MODEL="gpt-4o-mini"
VL_MODEL="gpt-4o"
CONCURRENT_NUMBER=8
```

😄 [AiHubMix招待リンク](https://aihubmix.com?aff=Gp54)を使用して登録してください 🌹

##### ローカルLLMサービスのデプロイ

Xinferenceを例にとると、.envの設定は以下のようになります：

```
# LLM_API_KEY='' ローカルサービスでは不要、コメントアウトまたは削除してください
LLM_API_BASE='http://127.0.0.1:9997' # ollamaの場合は 'http://127.0.0.1:11434/v1'
PRIMARY_MODEL=起動したモデルID
VL_MODEL=起動したモデルID
CONCURRENT_NUMBER=1 # 実際のハードウェアリソースに基づいて決定
```

#### 3. JINA_API_KEYの設定（検索エンジンサービス用）

https://jina.ai/ で取得、現在は登録なしで利用可能です。（高同時実行または商用利用の場合は、チャージしてください）

```
JINA_API_KEY=Your_API_KEY
```

#### 4. その他のオプション設定

以下はオプションの設定です：
- #VERBOSE="true" 

  観察モードを有効にするかどうか。有効にすると、デバッグ情報がロガーファイルに記録されます（デフォルトではコンソールにのみ出力）

- #CONCURRENT_NUMBER=8 

  LLMリクエストの同時実行数を制御するために使用。設定しない場合のデフォルトは1（有効にする前にLLMプロバイダーが設定された同時実行をサポートしていることを確認してください。ローカルの大規模モデルは、ハードウェア基盤に自信がある場合を除き、慎重に使用してください）

## 🐳 Dockerデプロイメント

バージョン4.xのDockerデプロイメントソリューションは今後の更新をお待ちください。また、興味のある開発者のPRの貢献もお待ちしています〜

## 🌹 有料サービス

オープンソースは簡単ではありません ☺️ ドキュメントの作成と相談Q&Aはさらに時間がかかります。サポートを提供していただければ、より良い品質のサービスを提供します〜

- 詳細なチュートリアル動画 + 3回のメール質疑応答 + 有料ユーザーWeChatグループへの参加：¥36.88

購入方法：以下の支払いコードをスキャンし、WeChat ID: bigbrother666sh を追加して、支払いのスクリーンショットを提供してください。

(フレンド申請は最長8時間以内に承認されます。メールアドレス 35252986@qq.com からも連絡可能です。)

<img src="alipay.png" alt="Alipay QRコード" width="300">      <img src="weixinpay.jpg" alt="WeChat Pay QRコード" width="300"> 