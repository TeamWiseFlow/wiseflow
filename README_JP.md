# AI チーフインテリジェンスオフィサー（Wiseflow）

**[English](README_EN.md) | [日本語](README_JP.md) | [한국어](README_KR.md) | [Deutsch](README_DE.md) | [Français](README_FR.md)**

🚀 **大規模言語モデルを使用して、日々の膨大な情報や様々なソースから、あなたが本当に興味のある情報を掘り起こしましょう！**

私たちに不足しているのは情報ではなく、膨大な情報からノイズをフィルタリングし、価値のある情報を引き出す能力です。

🌱 AIインテリジェンスオフィサーがどのように時間を節約し、無関係な情報をフィルタリングし、重要なポイントを整理するかを見てみましょう！🌱

https://github.com/user-attachments/assets/fc328977-2366-4271-9909-a89d9e34a07b

## 🔥🔥🔥 Wiseflow 4.0 バージョン正式リリース！

（オンラインサービスは現在技術的な理由により4.0コアに切り替わっていませんが、アップグレードを加速しています）

3ヶ月の待機期間を経て、ついにWiseflow 4.0バージョンの正式リリースを迎えました！

このバージョンでは、新しい4.xアーキテクチャを導入し、ソーシャルメディアソースのサポートを追加し、多くの新機能を提供します。

🌟 4.xにはWIS Crawler（Crawl4ai、MediaCrawler、Nodriverを基に深く再構築・統合）が含まれており、ウェブページとソーシャルメディアを完全にサポートしています。バージョン4.0では、まずWeiboとKuaishouプラットフォームのサポートを提供し、今後以下のプラットフォームを順次追加予定です：
WeChat公式アカウント、Xiaohongshu、Douyin、Bilibili、Zhihu...

4.xアーキテクチャがもたらすその他の新機能：

- 新しいアーキテクチャ、非同期とスレッドプールのハイブリッド使用により、処理効率を大幅に向上（メモリ消費も削減）
- Crawl4ai 0.6.3バージョンのディスパッチャー機能を継承し、より洗練されたメモリ管理を提供
- バージョン3.9のPre-ProcessとCrawl4aiのMarkdown Generationプロセスを深く統合し、重複処理を回避
- RSSソースのサポートを最適化
- リポジトリのファイル構造を最適化し、より明確で現代的なPythonプロジェクト標準に準拠
- uvを使用した依存関係管理に切り替え、requirement.txtファイルを最適化
- 起動スクリプトを最適化（Windowsバージョンを提供）、真の「ワンクリック起動」を実現
- 設定とデプロイメントプロセスを最適化、バックエンドプログラムはpocketbaseサービスに依存しなくなったため、.envでpocketbaseの認証情報を提供する必要がなく、pocketbaseのバージョン制限もありません

## 🧐 'ディープサーチ' VS 'ワイドサーチ'

私はWiseflowを「ワイドサーチ」として位置づけています。これは現在人気の「ディープサーチ」と対比されるものです。

具体的には、「ディープサーチ」は特定の質問に対してLLMが自律的に検索パスを計画し、異なるページを継続的に探索し、十分な情報を収集して回答やレポートを生成するものです。しかし、時には特定の質問を持たずに検索し、深い探索も必要とせず、広範な情報収集（業界インテリジェンス収集、背景情報収集、顧客情報収集など）だけが必要な場合があります。このような場合、広さが明らかに意味を持ちます。「ディープサーチ」でもこのタスクを達成できますが、それは大砲で蚊を打つようなもので、非効率で高コストです。Wiseflowはまさにこの「ワイドサーチ」シナリオのために特別に設計されたツールです。

## ✋ Wiseflowが他のAI駆動クローラーと異なる点は？

- ウェブページ、ソーシャルメディア（現在はWeiboとKuaishouプラットフォームをサポート）、RSSソース、検索エンジンなどを含む、フルプラットフォームの取得能力
- 単なるクローリングだけでなく、自動分析とフィルタリングを行い、14bパラメータのLLMで十分に機能
- ユーザーフレンドリー（開発者だけでなく）、コーディング不要、「すぐに使える」
- 継続的なイテレーションによる高い安定性と可用性、システムリソースと速度のバランスを考慮した処理効率
- （将来）insightモジュールを通じて、取得した情報の下に隠された「暗い情報」を掘り起こす能力

……… また、興味のある開発者の参加を期待し、誰もが使えるAIチーフインテリジェンスオフィサーを一緒に構築しましょう！

## 🚀 クイックスタート

**たった3ステップで始められます！**

### 📋 プロジェクトのソースコードをダウンロードし、uvとpocketbaseをインストール

- MacOS/Linux用：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

- Windows用：

**Windowsユーザーは事前にGit Bashツールをダウンロードし、bashで以下のコマンドを実行してください [Bashダウンロードリンク](https://git-scm.com/downloads/win)**

```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
git clone https://github.com/TeamWiseFlow/wiseflow.git
```

🌟 上記の操作でuvのインストールが完了します。pocketbaseのインストールについては、[pocketbase docs](https://pocketbase.io/docs/)を参照してください

install_pocketbase.sh（MacOS/Linux用）またはinstall_pocketbase.ps1（Windows用）を使用してインストールすることもできます。

### 📥 env_sampleを参考に.envファイルを設定

wiseflowフォルダ（プロジェクトのルートディレクトリ）でenv_sampleを参考に.envファイルを作成し、関連する設定情報を入力してください

### 🚀 起動！

- MacOS/Linux用：

```bash
cd wiseflow
./run.sh
```

（注意：最初に`chmod +x run.sh`を実行して実行権限を付与する必要があるかもしれません）

- Windows用：

```bash
cd wiseflow
.\run.ps1
```

（注意：最初に`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`を実行して実行権限を付与する必要があるかもしれません）

仮想ブラウザの起動に問題がある場合は、以下のコマンドを実行してください：

```bash
python -m playwright install --with-deps chromium
```

詳細な使用方法については、[docs/manual.md](./docs/manual.md)を参照してください

## 📚 Wiseflowでクロールしたデータを自分のプログラムで使用する方法

Wiseflowでクロールしたすべてのデータは即座にpocketbaseに保存されるため、pocketbaseデータベースを直接操作してデータを取得できます。

人気のある軽量データベースとして、PocketBaseは現在Go/Javascript/Pythonなどの言語のSDKを提供しています。

オンラインサービスはまもなくsync APIをリリースし、オンラインクロール結果をローカルに同期して「動的ナレッジベース」などを構築することをサポートします。お楽しみに：

  - オンライン体験アドレス：https://www.aiqingbaoguan.com/
  - オンラインサービスAPI使用例：https://github.com/TeamWiseFlow/wiseflow_plus

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

このプロジェクトの開発は[GNE](https://github.com/GeneralNewsExtractor/GeneralNewsExtractor)、[AutoCrawler](https://github.com/kingname/AutoCrawler)、[SeeAct](https://github.com/OSU-NLP-Group/SeeAct)に触発されています。

## 引用

関連する作業でこのプロジェクトの一部または全部を参照または引用する場合は、以下の情報を記載してください：

```
著者：Wiseflow Team
https://github.com/TeamWiseFlow/wiseflow
Apache2.0ライセンス
``` 