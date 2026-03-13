# QUESTION 24

Tasks:
Troubleshoot R-WEST to achieve the desired results:

1. All the changes to the running-config must be locally archived except passwords which must be suppressed. All passwords must be encrypted.
2. Only the Cisco specific OSPF LSA traps should be sent to the SNMP server.

QUESTION 24 は、R-WEST で「コンフィグ変更のローカルアーカイブ」と「OSPF LSA の Cisco固有 SNMP トラップ」の2つだけ直す問題です。

***

## 要件の整理

既存の主な設定（抜粋）[^1]

- R-WEST:
    - Loopback0 と e0/0 に IPv4 アドレス
    - `router ospf 10`（connected を再配布）
    - `logging host 10.1.100.14 sequence-num-session`（Syslog サーバ宛）
    - `snmp-server community public RO`
    - `snmp-server host 10.2.100.161 public`（SNMP サーバ）


### Task 1

1. running-config への「すべての変更」をローカルにアーカイブ。
2. その際、パスワードはログに出さない（suppress）。
3. running-config 上のパスワードはすべて暗号化。

### Task 2

- SNMP サーバには「Cisco specific OSPF LSA traps」だけ送る。

***

## 必要なコマンド

### Task 1：ローカルアーカイブ + パスワード暗号化

**R-WEST**

```plaintext
enable
configure terminal
service password-encryption
archive
 log config
  logging enable
  hidekeys
end
copy run start
```

**解説：**

- `service password-encryption`
    - running-config に保存される `password` や `community` などの平文パスワードをタイプ7で暗号化。[^1]
- `archive` 以下の設定
    - `log config`：コンフィグ変更ログ機能を有効化するモードに入る。
    - `logging enable`：コンフィグ変更が起きたときにログへ出す。ローカル logging が有効なので、これで「ローカルにアーカイブ」される。
    - `hidekeys`：ログに出るコマンドの中で、パスワードやキーを伏せ字にして記録（suppress）。

`show archive log config all` で、実際にどのコマンドが記録されているか確認できる。

***

### Task 2：Cisco specific OSPF LSA トラップ

**R-WEST**

```plaintext
enable
configure terminal
snmp-server enable traps ospf cisco-specific lsa
end
copy run start
```

**解説：**

- `snmp-server enable traps ospf ...` は OSPF 関連イベントを SNMP トラップとして送る機能。
- `cisco-specific lsa` を付けることで、一般的な OSPF トラップではなく Cisco 拡張の LSA 関連トラップだけを有効にする。[^1]
- SNMP サーバ自体は既に `snmp-server host 10.2.100.161 public` で定義済みなので、そのまま利用。

***

この問題で新しめの概念は「archive log config の hidekeys」だと思いますが、今の説明でイメージはつきましたか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

