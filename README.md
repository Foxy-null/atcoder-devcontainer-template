# AtCoder Dev Container

AtCoder・yukicoder向けのC++開発環境です。コンパイラや問題取得ツールをコンテナにまとめ、Windows＋WSL2とGitHub Codespacesで使えます。

**Ubuntu 24.04 / C++23 / GCC 15.2.0 / GDB / AtCoder向けの全12ライブラリ / atcoder-cli / online-judge-tools / aclogin** を収録しています。設定ファイル内のユーザー名・保存先・リポジトリ名を書き換える必要はありません。

GCCとライブラリはAtCoderの公式一覧（2026年6月16日更新）に合わせて固定しています。初回はソースからの構築を含むため時間がかかります。メモリ8GB以上・空き容量32GB以上を用意してください。詳しいバージョンと構築条件は[メンテナンスガイド](docs/maintenance.md)にまとめています。

## 1. セットアップ・起動

### Windows＋WSL2

事前に次を用意します。

- [WSL2](https://learn.microsoft.com/windows/wsl/install)（Ubuntuなど）と、WSL内のGit
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)（**Settings → Resources → WSL Integration** で使用するディストリビューションを有効にします）
- Windows版[VS Code](https://code.visualstudio.com/)と、**WSL**・**Dev Containers** 拡張機能

#### 初回セットアップ

1. このテンプレートから自分用のリポジトリを作成します（**Use this template** または **Fork**）。
2. Docker Desktopを起動します。
3. **WSLのターミナル**で以下を実行します。URLは自分のリポジトリのURLに置き換えてください。

   ```bash
   mkdir -p ~/projects
   cd ~/projects

   # atcoder-workspaceディレクトリにクローン
   git clone https://github.com/<あなたのGitHubユーザー名>/<作成したリポジトリ名>.git atcoder-workspace
   cd atcoder-workspace
   code .
   ```

4. VS Codeで **F1 → Dev Containers: Reopen in Container** を実行します。
5. 初回ビルドとセットアップが終わり、ログに **AtCoder toolchain OK** と表示されれば準備完了です。

> [!TIP]
> この例では `~/projects/atcoder-workspace` にクローンしていますが、クローン先はWSL内の任意のディレクトリで構いません。導入の詳細は[VS Code公式ガイド](https://code.visualstudio.com/docs/devcontainers/containers)を参照してください。

<details>
  <summary>2回目以降の起動</summary>

Docker Desktopを起動し、WSLのターミナルで以下を実行します。クローン先を変更した場合は、パスを読み替えてください。

   ```bash
   # クローン済みのディレクトリに移動
   cd ~/projects/atcoder-workspace

   # VS Codeを起動
   code .
   ```

コンテナ内で開かれない場合は、VS Codeで **F1 → Dev Containers: Reopen in Container** を実行します。

</details>

### GitHub Codespaces

1. このテンプレートから自分用のリポジトリを作成します（**Use this template** または **Fork**）。
2. 自分のリポジトリで **Code → Codespaces → Create codespace** を選びます。
3. 初回ビルドとセットアップが終わり、ターミナルに **Finished configuring codespace.** が表示されれば準備完了です。

ローカルへのDocker・VS Codeのインストールは不要です。

## 2. ログイン

利用するサービスの手順に従ってログインします。以下のコマンドは、すべて**コンテナ内のターミナル**で実行してください。

### AtCoder

以下のコマンドを実行します。

```bash
aclogin
```

ブラウザで[AtCoder](https://atcoder.jp)にログインし、開発者ツールの **Application（FirefoxではStorage）→ Cookies → https://atcoder.jp → REVEL_SESSION** の値をコピーして、プロンプトに貼り付けます。

この値はログイン情報です。他人と共有したり、Gitに追加したりしないでください。認証情報はコンテナ用のボリュームに保存され、通常の再ビルドでは保持されます。別のCodespaceや別の導入方法では再ログインが必要です。

### yukicoder

1. 以下のコマンドを実行します。

   ```bash
   oj login https://yukicoder.me/
   ```

2. 次の画像のようなエラーでログインできない場合は、コンテナ内のVS Codeで `config/online-judge-tools/cookie.jar` を開きます。ログインに成功した場合は、以降の操作は不要です。

   <details>
     <summary>ログイン時のエラー例</summary>
     <img width="776" height="287" alt="yukicoderへのログイン時に表示されるエラー例" src="https://github.com/user-attachments/assets/46e7d726-dccc-4b73-b482-cb1c408423ee" />
   </details>

3. ブラウザで[yukicoder](https://yukicoder.me)にログインします。開発者ツールの **Application（FirefoxではStorage）→ Cookies → https://yukicoder.me → REVEL_SESSION** の値をコピーします。
4. `cookie.jar` 内で、`domain=yukicoder.me` を含む `Set-Cookie3: REVEL_SESSION=...` の行を探します。`REVEL_SESSION=` の直後から次の `;` までの値だけを、コピーした値に置き換えて保存します。他の項目は変更しないでください。

`cookie.jar` にもログイン情報が含まれます。他人と共有したり、Gitに追加したりしないでください。

## 3. 問題を解く

**F1 → Tasks: Run Task（タスク: タスクの実行）** でタスクを選びます。

> [!TIP]
> **Tasks: Run Task（タスク: タスクの実行）** にキーボードショートカットを割り当てると、タスク一覧をすばやく開けます。設定方法は[補足ガイド](docs/options.md#タスク一覧のショートカット)を参照してください。
>
> <img width="530" height="88" alt="タスク一覧を開くキーボードショートカットの設定例" src="https://github.com/user-attachments/assets/8a47ba6f-c29d-48ac-9fbc-3c533a25c1a9" />

| やりたいこと | 操作 |
| --- | --- |
| AtCoderの問題を取得 | `Download from AtCoder` → コンテストID（例：`practice`）またはURLを入力し、問題を選択 |
| yukicoderの問題を取得 | `Download from yukicoder` → 問題番号を入力 |
| ビルド・サンプルテスト | `main.cpp` を開いて **Ctrl+Shift+B** |
| デバッグ | `main.cpp` を開いて **F5**（Sample 1〜3は対応するサンプルがある問題で使用） |
| 提出 | `main.cpp` を開き、タスク一覧から `submit to AtCoder (C++)` または `submit to yukicoder (C++)` を選択 |

- AtCoderの問題は `atcoder/<カテゴリ>/<コンテストID>/<問題>/`、yukicoderの問題は `yukicoder/<問題番号>/` に保存されます。AtCoderの問題URLを入力した場合も、コンテストから取得する問題を選びます。
- C++の雛形は [`config/atcoder-cli/cpp/main.cpp`](config/atcoder-cli/cpp/main.cpp) を編集すると、次の問題取得から反映されます。
- ACLは `#include <atcoder/all>` で利用できます。
- Boostは `#include <boost/dynamic_bitset.hpp>` などで利用できます。ビルド・デバッグのタスクには、全ライブラリの参照先とリンク設定が含まれます。
- ターミナルからビルドするときは `atcoder-g++ main.cpp -o a.out` を使います。デバッグ用は `atcoder-g++ -g -O0 main.cpp -o a.out` です。

> [!NOTE]
> AtCoderの問題は、ダウンロード時に次の **10カテゴリ**へ自動で振り分けられます。
>
> - **コンテスト別**：`ABC`・`ARC`・`AGC`・`AHC`・`ADT`・`PAST`・`JOI`・`AWC`
> - **`TRAINING`**：練習・学習用（APG4b、ABS、競プロ典型90問、競技プログラミングの鉄則、DPまとめコンテストなど）
> - **`OTHER`**：上記の分類に該当しないコンテスト
>
> <img width="446" alt="カテゴリ別の保存フォルダー例" src="https://github.com/user-attachments/assets/671b962e-564a-4d26-9443-a72499e64915" />

## 困ったとき・カスタマイズ

- **セットアップの確認**：コンテナ内で `verify-atcoder-toolchain` を実行します。
- **Dockerへ接続できない**：Docker Desktopの起動状態とWSL Integrationを確認します。
- **認証が切れた**：「[ログイン](#2-ログイン)」の該当サービスの手順に従って、ログイン情報を更新します。
- **環境を更新したい**：F1から `Dev Containers: Rebuild Container` または `Codespaces: Rebuild Container` を実行します。
- **テーマ・キー割り当て・Composeでの起動**：任意設定をまとめた[補足ガイド](docs/options.md)を参照してください。

`#include` エラーが出る場合は、まずVS Codeをコンテナ内で開いていることを確認してください。古いコンテナを使用している場合は再ビルドし、`verify-atcoder-toolchain` を実行します。コンテナにヘッダーがない状態では、`includePath` を増やすだけでは直りません。

固定しているツールのバージョンと検証手順は[メンテナンスガイド](docs/maintenance.md)を参照してください。

## ライセンス

[MIT](LICENSE)。コンテナにインストールする各ツールには、それぞれのライセンスが適用されます。
