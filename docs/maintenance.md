# メンテナンス

## 固定バージョン

| ツール | バージョン |
| --- | --- |
| atcoder-cli | 2.2.0 |
| online-judge-tools | 11.5.1 |
| aclogin | 0.2.1 |
| GCC | 15.2.0 |
| Abseil | 20250512.1 |
| AtCoder Library | 1.6 |
| Boost | 1.88.0 |
| Eigen | 3.4.0 |
| GMP | 6.3.0 |
| immer | 0.8.1 |
| LibTorch（CPU） | 2.8.0 |
| LightGBM | 4.6.0 |
| OR-Tools | 9.14 |
| range-v3 | 0.12.0 |
| unordered_dense | 4.5.0 |
| Z3 | 4.15.2 |

CLIツールの更新時は `.devcontainer/Dockerfile` と `.devcontainer/scripts/verify-atcoder-toolchain` の値を揃えてください。新しいイメージの検証後、`.devcontainer/devcontainer.json` と `.devcontainer/Dockerfile.prebuilt` のダイジェストを同時に更新します。

GCCとライブラリは、[公式一覧](https://img.atcoder.jp/file/language-update/2025-10/language-list.html)の2026年6月16日更新版を基準にしています。[公式GCCスクリプト](https://img.atcoder.jp/file/language-update/2025-10/017-23_gcc_14-2-0.toml)を `.devcontainer/atcoder/gcc.toml` に保存し、SHA-256で変更を検出します。スクリプトのライセンスはCC0-1.0です。ファイル名に14.2.0とありますが、内容は15.2.0です。

更新時は公式告知とスクリプトの差分を読み、保存版・`prepare.py`のハッシュ・動作確認コード・この表を更新してください。日付を含まない[旧一覧](https://img.atcoder.jp/file/language-update/language-list.html)は2023年版です。2026年6月には[コンパイル設定からLTOを削除する更新](https://atcoder.jp/posts/language_update20260616_jp)もあり、バージョン番号だけでなく設定の確認も必要です。

## 構築と実行

Ubuntu 24.04のベースイメージをダイジェストで固定しています。GCCと12ライブラリは公式レシピのバージョンを使い、OR-Toolsの依存ライブラリ・ソルバーも同じビルド設定で導入します。OSの全パッケージやCPU、ジャッジの時間・メモリ制限まで完全再現する構成ではありません。Windows＋WSL2・Codespacesのx86-64向けです。macOS・ARM環境はサポート対象に含めていません。

公式レシピからの調整は、rootでの実行、GCC取得先のHTTPS化、並列数の制限、構築工程の分割です。OR-Tools 9.14が内部依存として構築するBoost 1.87は公開先も上書きするため、OR-Toolsの後に公式レシピのBoost工程をもう一度実行して1.88.0へ戻します。公開されるBoostヘッダーのバージョンはコンテナ検証で確認します。標準ライブラリのモジュールキャッシュは生成しません。このテンプレートの検証対象は `#include` を使うコードです。

初回の構築には時間がかかり、メモリ8GB以上・空き容量32GB以上が必要です。既定の並列数はGCCとOR-Toolsが4、その他のライブラリが2です。Dockerのビルド引数 `COMPILER_BUILD_JOBS`・`OR_TOOLS_BUILD_JOBS`・`BUILD_JOBS` で調整できます。GCCとOR-Toolsのコンパイル途中のデータもBuildKitキャッシュに保存します。工程ごとのDockerキャッシュにより、タスク設定や雛形の変更だけでGCCを再構築する必要はありません。

`.devcontainer/Dockerfile` を配布イメージの正本として、GitHub Actionsが `linux/amd64` の候補イメージをGHCRへ発行します。候補は `ghcr.io/foxy-null/atcoder-devcontainer-template:candidate` と、同じ内容を指す上書きされない `sha-<commit>-<run>-<attempt>` タグです。候補を2 CPU・4GBメモリに制限してこのリポジトリのコンテナ検証を通し、来歴をattestationとして登録します。`main` 上で全検証に成功した場合だけ、同じダイジェストを `stable` に昇格します。

Dev Containers・Codespacesは検証済みイメージを直接使用します。Composeは `.devcontainer/Dockerfile.prebuilt` で同じイメージのUID/GIDだけを調整します。いずれもダイジェスト固定のため、`stable` の更新だけでは利用環境は変わりません。新しい配布版は検証後に両方の参照を更新してください。ロールバック時も両方を以前のダイジェストへ戻して再構築します。

ローカルで正本から明示的に構築する場合は、リポジトリのルートで次を実行します。この場合は従来どおり、初回構築用にメモリ8GB以上を確保してください。

```bash
docker buildx build --load --platform linux/amd64 \
  --file .devcontainer/Dockerfile \
  --tag atcoder-devcontainer:source .
```

ワークフローはmainへの環境を変えるファイルのpush、手動実行、毎月2日3:17（日本時間）の完全再構築で動きます。PRとテンプレートから派生したリポジトリでは軽量な構成検証だけを行い、GHCRへの発行は元のテンプレートリポジトリに限定します。

Ubuntu配布サーバーに接続できない場合は、ビルド引数 `UBUNTU_MIRROR` にUbuntuのミラーURLを指定できます（例：`http://ftp.jaist.ac.jp/pub/Linux/ubuntu/`）。パッケージの署名検証は維持します。

コンパイラとヘッダーは `/opt/atcoder/gcc` に配置します。`atcoder-g++` が公式レシピから生成したコンパイル・リンク設定を適用し、通常ビルド・デバッグ・環境検証で共用します。`-g -O0` を渡すとデバッグ向けに最適化を上書きできます。通常の `g++` は同じGCC 15.2.0ですが、外部ライブラリ用のオプションを自動追加しません。

VS Codeの補完も同じコンパイラ・ヘッダー・マクロを使います。`C_Cpp.default.*` と `.vscode/c_cpp_properties.json` の設定を揃え、`tests/check-portability.py` で不一致を検出します。

AtCoderへの提出言語は **C++23 (GCC 15.2.0)** を選んでください。yukicoderの提出先に同じライブラリがあるとは限りません。

## 検証

Python 3.11以上とBashがある環境で、リポジトリのルートから実行します。外部サービスへのログイン・問題取得・提出は行いません。

```bash
python3 tests/check-portability.py
```

JSONとシェルの構文、既存のワークフロー検証、空白や記号を含むパスでのタスク実行、不正な問題番号の拒否、再ダウンロード時の編集済みコード保持を確認します。外部コマンドはテスト用の代替に置き換えるため、実際のコンテナ確認も必要です。

Windows＋WSL2では、通常と異なるリポジトリ名でクローンしてDev Containerを開き、次を確認します。Codespacesでも別名のリポジトリから同じ確認を行います。

```bash
verify-atcoder-toolchain
python tests/check-portability.py
```

全12ライブラリのコンパイル・リンク・実行、OR-Toolsのソルバー、サンプルテストとGDBまでまとめて確認する場合は、コンテナ内で次を実行します。

```bash
bash tests/check-container.sh
```

続いて、ログイン・問題取得・Ctrl+Shift+B・F5を手動で確認します。提出タスクの動作確認は、自分で提出先とソースを確認したうえで行ってください。

Docker Composeの確認は[補足ガイド](options.md#docker-composeだけで起動する)を参照してください。

## 参考

- [Dev Container仕様](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainerjson-reference.md)
- [atcoder-cli](https://github.com/Tatamo/atcoder-cli)
- [online-judge-tools](https://github.com/online-judge-tools/oj)
- [aclogin](https://github.com/key-moon/aclogin)
- [AtCoder Library](https://github.com/atcoder/ac-library)
