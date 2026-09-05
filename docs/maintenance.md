# メンテナンス

## 固定バージョン

| ツール | バージョン |
| --- | --- |
| atcoder-cli | 2.2.0 |
| online-judge-tools | 11.5.1 |
| aclogin | 0.2.1 |
| AtCoder Library | v1.6 |

更新時は `.devcontainer/Dockerfile`・`.devcontainer/devcontainer.json`・`compose.yaml`・`.devcontainer/scripts/verify-atcoder-toolchain` の値を揃えてください。ACLのコミットIDも一致させます。

Arch LinuxのOSパッケージは固定していません。Windows＋WSL2・Codespaces向けの構成です。macOS・ARM環境はサポート対象に含めていません。

## 検証

Python 3とBashがある環境で、リポジトリのルートから実行します。外部サービスへのログイン・問題取得・提出は行いません。

```bash
python3 tests/check-portability.py
```

JSONとシェルの構文、既存のワークフロー検証、空白や記号を含むパスでのタスク実行、不正な問題番号の拒否、再ダウンロード時の編集済みコード保持を確認します。外部コマンドはテスト用の代替に置き換えるため、実際のコンテナ確認も必要です。

Windows＋WSL2では、通常と異なるリポジトリ名でクローンしてDev Containerを開き、次を確認します。Codespacesでも別名のリポジトリから同じ確認を行います。

```bash
verify-atcoder-toolchain
python tests/check-portability.py
```

続いて、ログイン・問題取得・Ctrl+Shift+B・F5を手動で確認します。提出タスクの動作確認は、自分で提出先とソースを確認したうえで行ってください。

Docker Composeの確認は[補足ガイド](options.md#docker-composeだけで起動する)を参照してください。

## 参考

- [Dev Container仕様](https://github.com/devcontainers/spec/blob/main/docs/specs/devcontainerjson-reference.md)
- [atcoder-cli](https://github.com/Tatamo/atcoder-cli)
- [online-judge-tools](https://github.com/online-judge-tools/oj)
- [aclogin](https://github.com/key-moon/aclogin)
- [AtCoder Library](https://github.com/atcoder/ac-library)
