# 任意設定

## テーマ・表示言語

テーマや表示言語はVS Codeの設定から自由に変更できます。Pitch Blackを使う場合は拡張機能 **Pitch Black Theme**（`viktorqvarfordt.vscode-pitch-black-theme`）をインストールし、**Preferences: Color Theme** から選択します。日本語表示は **Japanese Language Pack** で追加できます。

## タスク一覧のショートカット

F1から **Preferences: Open Keyboard Shortcuts (JSON)** を開き、既存の配列に次の項目を追加します。

```json
{
  "key": "ctrl+shift+v",
  "command": "workbench.action.tasks.runTask"
}
```

この設定を追加すると、同じキーの既存の割り当てより優先される場合があります。既存設定全体を上書きせず、好きなキーを指定してください。

## Docker Composeだけで起動する

VS Code Dev Containersを使わず、ターミナルで作業したい場合の手順です。**WSLのターミナルで、リポジトリのルートから**実行します。

.envが既にある場合は、次のコマンドで上書きせず、LOCAL_UIDとLOCAL_GIDだけを変更してください。

```bash
printf 'LOCAL_UID=%s\nLOCAL_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
docker compose exec atcoder verify-atcoder-toolchain
docker compose exec atcoder bash
```

`.env`が既にある場合は上書きせず、`LOCAL_UID`と`LOCAL_GID`だけ更新してください。VS Code Dev Containers経由ならこの設定は不要です。

コンテナ内で初回ログインと問題取得を行います。

```bash
aclogin
atcoder-workflow download practice "$PWD"
```

ホスト側のフォルダー名にかかわらず、Compose内では `/workspace` に配置されます。Dev Containers・Codespacesとは認証用volumeを共有しません。同名のフォルダーを複数使う場合は `.env` に異なる `COMPOSE_PROJECT_NAME` を指定してください。

停止する場合は、WSLのリポジトリルートで `docker compose down` を実行します。`docker compose down -v` はログイン情報を含むvolumeも削除します。

## 設定と認証情報の場所

- C++雛形：`config/atcoder-cli/cpp/main.cpp`
- ACC既定設定：`config/atcoder-cli/config.json`（変更後はコンテナを再ビルド）
- ACC認証の保存先：コンテナ内で `acc config-dir` を実行して確認
- OJ認証の通常の保存先：`/home/vscode/.local/share/online-judge-tools/cookie.jar`

セットアップは認証情報の原本へのリンクを `config/atcoder-cli/session.json` と `config/online-judge-tools/cookie.jar` に作ります。ログイン前はリンク先のファイルがありません。認証ファイルと `.env` はGitとDockerビルドの対象外です。
