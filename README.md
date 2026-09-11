# AtCoder Dev Container

AtCoder・yukicoder向けのC++開発環境です。コンパイラや問題取得ツールをコンテナにまとめ、Windows＋WSL2とGitHub Codespacesで使えます。

**C++23 / GCC / GDB / AtCoder Library / atcoder-cli / online-judge-tools / aclogin** を収録。ユーザー名・保存先・リポジトリ名の書き換えは不要です。

## 1. セットアップ・起動

### Windows＋WSL2

事前に次を用意します。

- [WSL2](https://learn.microsoft.com/windows/wsl/install)（Ubuntuなど）と、WSL内のGit
- [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/)：起動し、**Settings → Resources → WSL Integration** で使用するディストリビューションを有効化
- Windows版[VS Code](https://code.visualstudio.com/)と、**WSL**・**Dev Containers** 拡張機能

1. このテンプレートから自分用のリポジトリを作成（**Use this template**、またはFork）する。
2. **WSLのターミナル**で以下を実行する。URLは作成した自分のリポジトリのものに置き換えること。
> [!tip]
> 下記では`projects`ディレクトリを作成していますが、保存先はWSL内の任意のフォルダーで構いません。導入の詳細は[VS Code公式ガイド](https://code.visualstudio.com/docs/devcontainers/containers)を参照してください。

   ```bash
   # ディレクトリを作成（任意）
   mkdir -p ~/projects

   # 作成した（或いはクローン先の任意のディレクトリ）に移動
   cd ~/projects

   # 初回セットアップ時のみ実行
   # 例では~/projects/atcoder-workspace/...にクローンされます
   git clone https://github.com/<あなたのGitHubユーザー名>/<作成したリポジトリ名>.git atcoder-workspace
   
   cd atcoder-workspace

   # VS Codeを起動
   code .
   ```
3. Docker desktopを起動する。
4. VS Codeで **F1 → Dev Containers: Reopen in Container** を実行する。
5. 初回ビルドが終わり、セットアップログに **AtCoder toolchain OK** と表示されれば準備完了です。

### GitHub Codespaces

1. このテンプレートから自分用のリポジトリを作成します（**Use this template**、またはFork）。
2. 自分のリポジトリで **Code → Codespaces → Create codespace** を選びます。
3. 初回ビルドとセットアップが終わったら、ターミナルで `verify-atcoder-toolchain` を実行します。**AtCoder toolchain OK** が表示されれば準備完了です。

ローカルへのDocker・VS Codeのインストールは不要です。

## 2. AtCoderにログイン

**コンテナ内のターミナル**で実行します。

```bash
aclogin
```

ブラウザでAtCoderにログインし、開発者ツールの **Application（FirefoxではStorage）→ Cookies → https://atcoder.jp → REVEL_SESSION** の値をコピーして、プロンプトに貼り付けます。

この値はログイン情報です。共有・Gitへの追加はしないでください。認証情報はコンテナ用volumeへ保存され、通常の再ビルドでは保持されます。別のCodespaceや別の導入方法では再ログインが必要です。

## 3. 問題を解く

**F1 → Tasks: Run Task（タスク: タスクの実行）** でタスクを選びます。

> [!Tip]
> **Tasks: Run Task（タスク: タスクの実行）**にキーバインドを設定するとアクセスしやすくなります（以下は一例）
> <img width="530" height="88" alt="Screenshot 2026-09-09 003913" src="https://github.com/user-attachments/assets/8a47ba6f-c29d-48ac-9fbc-3c533a25c1a9" />




| やりたいこと | 操作 |
| --- | --- |
| AtCoderの問題を取得 | `Download from AtCoder` → コンテストID（例：`practice`）またはURLを入力し、問題を選択 |
| yukicoderの問題を取得 | `Download from yukicoder` → 問題番号を入力 |
| ビルド・サンプルテスト | `main.cpp`を開いて **Ctrl+Shift+B** |
| デバッグ | `main.cpp`を開いて **F5**（Sample 1〜3は対応するサンプルがある問題で使用） |
| 提出 | `main.cpp`を開いて `submit to AtCoder (C++)` または `submit to yukicoder (C++)` |

AtCoderの問題は `atcoder/<カテゴリ>/<コンテストID>/<問題>/`、yukicoderの問題は `yukicoder/<問題番号>/` に保存されます。AtCoderの問題URLを入力した場合も、コンテストから取得する問題を選びます。

C++の雛形は [`config/atcoder-cli/cpp/main.cpp`](config/atcoder-cli/cpp/main.cpp) を編集すると、次の問題取得から反映されます。ACLは `#include <atcoder/all>` で利用できます。

## 困ったとき・カスタマイズ

- **セットアップの確認**：コンテナ内で `verify-atcoder-toolchain` を実行します。
- **Dockerへ接続できない**：Docker Desktopの起動状態とWSL Integrationを確認します。
- **認証が切れた**：コンテナ内で `aclogin` を実行し、ログイン情報を更新します。
- **環境を更新したい**：F1から `Dev Containers: Rebuild Container` または `Codespaces: Rebuild Container` を実行します。
- **テーマ・キー割り当て・Composeでの起動**：任意設定をまとめた[補足ガイド](docs/options.md)を参照してください。

Arch LinuxのOSパッケージは再ビルド時に更新されます。固定しているツールのバージョンと検証手順は[メンテナンスガイド](docs/maintenance.md)を参照してください。

## ライセンス

[MIT](LICENSE)。コンテナにインストールする各ツールには、それぞれのライセンスが適用されます。
