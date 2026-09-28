# 任意設定

## テーマ・表示言語

テーマや表示言語はVS Codeの設定から自由に変更できます。Pitch Blackを使う場合は拡張機能 **Pitch Black Theme**（`viktorqvarfordt.vscode-pitch-black-theme`）をインストールし、**Preferences: Color Theme** から選択します。日本語表示は **Japanese Language Pack** で追加できます。

## タスク一覧のショートカット

`Ctrl+Shift+V` によるタスク一覧の表示は、このテンプレートでは自動設定されません。キー割り当てはVS Codeのユーザー設定です。ブラウザ版Codespacesでローカルの設定が同期されていない場合は、**Codespaces側で** F1から **Preferences: Open Keyboard Shortcuts (JSON)** を開き、既存の配列に次の項目を追加して保存します。

```json
{
  "key": "ctrl+shift+v",
  "command": "workbench.action.tasks.runTask"
}
```

この設定を追加すると、同じキーの既存の割り当てより優先される場合があります。既存設定全体を上書きせず、好きなキーを指定してください。

ローカルと同じキー割り当てを使う場合は、[Settings SyncをCodespacesで有効にする](https://docs.github.com/en/codespaces/setting-your-user-preferences/personalizing-github-codespaces-for-your-account)方法もあります。コンテナの再ビルドは不要です。

## Docker Composeだけで起動する

VS Code Dev Containersを使わず、ターミナルで作業したい場合の手順です。**WSLのターミナルで、リポジトリのルートから**実行します。

.envが既にある場合は、次のコマンドで上書きせず、LOCAL_UIDとLOCAL_GIDだけを変更してください。

```bash
printf 'LOCAL_UID=%s\nLOCAL_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
docker compose exec atcoder verify-atcoder-toolchain
docker compose exec atcoder bash
```

`.env`が既にある場合は上書きせず、`LOCAL_UID`と`LOCAL_GID`だけ更新してください。ビルド済みイメージ上でUID/GIDだけを調整するため、GCCの再構築は行いません。VS Code Dev Containers経由ならこの設定は不要です。既存の認証volumeを使う場合はUID/GIDを途中で変更しないでください。

コンテナ内で初回ログインと問題取得を行います。

```bash
aclogin
atcoder-workflow download practice "$PWD"
```

ホスト側のフォルダー名にかかわらず、Compose内では `/workspace` に配置されます。Dev Containers・Codespacesとは認証用volumeを共有しません。同名のフォルダーを複数使う場合は `.env` に異なる `COMPOSE_PROJECT_NAME` を指定してください。

停止する場合は、WSLのリポジトリルートで `docker compose down` を実行します。`docker compose down -v` はログイン情報を含むvolumeも削除します。

## 設定と認証情報の場所

- C++雛形：`config/atcoder-cli/cpp/main.cpp`
- C++雛形の展開設定：`config/atcoder-cli/cpp/template.json`（変更は次回取得から反映）
- ACC既定設定：`config/atcoder-cli/config.json`（変更後は配布イメージを発行し、参照ダイジェストを更新してコンテナを再構築）
- ACC認証の保存先：コンテナ内で `acc config-dir` を実行して確認
- OJ認証の通常の保存先：`/home/vscode/.local/share/online-judge-tools/cookie.jar`

セットアップは認証情報の原本へのリンクを `config/atcoder-cli/session.json` と `config/online-judge-tools/cookie.jar` に作ります。ログイン前はリンク先のファイルがありません。認証ファイルと `.env` はGitとDockerビルドの対象外です。

ACCの `cpp` ディレクトリはリポジトリの雛形ディレクトリを参照します。`main.cpp` 自体は通常ファイルにしてください。雛形の編集は新しく取得する問題だけに反映され、既存の解答は変更されません。旧設定は初期化時にACC設定領域の `cpp.backup.XXXXXX/cpp` に退避されます。以前その領域で独自編集した雛形・展開設定があれば、退避先と比較してリポジトリ側へ取り込んでください。

## 既存の解答リンクの修復

以前の配布版には、各問題の `main.cpp` が同じC++雛形へのリンクになる不具合がありました。修正版を取り込んでコンテナを再構築しても、取得済みの解答リンクは残ります。

コンテナ内のリポジトリルートで、まず対象を確認します。

```bash
python3 .devcontainer/atcoder/migrate-solution-links.py "$PWD"
```

対象は `atcoder/` 配下で、このリポジトリのC++雛形を指す `main.cpp` です。通常ファイルと無関係なリンクは変更しません。`SKIP` と表示された未知のリンクや切れたリンクは個別確認が必要なため、コマンドは終了コード1を返します。

解答の編集・問題取得を止め、**雛形の内容を戻す前に**次を実行します。

```bash
python3 .devcontainer/atcoder/migrate-solution-links.py "$PWD" --apply
```

現在の内容とリンク先情報を `.solution-link-backup-*/` に保存した後、対象を同じ内容の独立した通常ファイルに置き換えます。`SKIP` があっても他の対象は修復されます。再実行しても修復済みの通常ファイルは変更しません。バックアップはGitの対象外です。

リンク共有で過去に上書きされた問題ごとの解答は、この処理では復元できません。Git・VS Codeのローカル履歴・AtCoderの提出履歴などから復旧してください。移動したリポジトリを指す切れたリンクも、自動で内容を推測せず個別に復旧してください。
