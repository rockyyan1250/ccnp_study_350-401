# QUESTION 18
Tasks:
Troubleshoot and resolve the issues on West and East routers to achieve these goals. The username/password and enable password is 'cisco' on all devices.

1. Ensure that the west router authorizes remote users over ssh to use a local database matching username as "westadmin" and the password is "westadminpass".
Generate RSA 2048 bit key. Modify the existing aaa policy name for configuration.
2. Ensure that the ping is permitted to the east router daily from 9:00 AM to 6:00 PM only. Complete the task using a preconfigured access list; do not add any deny
entries.

QUESTION 18 は AAA/SSH と ACL+time-range の組み合わせです。

***

## Topology と前提

- West ルータ：
    - e0/0 = 192.168.20.1/24（SW2 側 LAN）
    - e0/1 = 20.0.20.2/30（ISP 側）
- East ルータ：
    - e0/0 = 192.168.10.1/24（SW1 側 LAN）
    - e0/1 = 10.0.10.2/30（ISP 側）

既存設定（抜粋）[^1]

- West:
    - `ip domain-name cisco.com`
    - `aaa new-model`
    - `aaa authentication login default local-case none`
    - `aaa authentication login SSH_Connections local none`
    - line vty 0 4 は `transport input all` のみ（login 認証リスト未適用）
- East:
    - e0/1 に `ip access-group icmp-rule in`
    - ACL `icmp-rule` に `deny icmp any any time-range blkicmp`
    - time-range `blkicmp` は `periodic daily 18:01 to 23:59`
    - 他に permit エントリなし（＝それ以外の時間も implicit deny）

***

## タスク文の翻訳と意味

1.「West では SSH で入ってくるリモートユーザを、ローカル DB の `westadmin/westadminpass` で認証するようにしなさい。RSA 2048bit 鍵を生成し、既存の AAA ポリシー名を修正して使うこと。」
→ SSH 有効化（RSA鍵）、ユーザ作成、`aaa authentication login SSH_Connections` を `local` のみにし、VTY ラインでそのリストを使用する。[^1]

2.「East では、ping が 9:00〜18:00 の間だけ許可されるようにしなさい。あらかじめ用意された ACL を使い、deny エントリは追加してはならない。」
→ 既存 time-range `blkicmp` を「禁止時間帯（0:00-8:59,18:01-23:59）」にし、ACL に 1つだけ permit 行を追加して「それ以外（=9:00〜18:00）」を許可する。[^1]

***

## 作業前に確認すべきポイント

### West

1. `show run | section aaa`
    - default と `SSH_Connections` の login リスト内容を確認（末尾に `none` がある）。
2. `show run | section vty`
    - VTY でどの authentication list も使っていないことを確認。
3. `show crypto key mypubkey rsa`
    - 既に RSA 鍵があるかチェック（なければ生成が必要）。

### East

1. `show run interface e0/1`
    - `ip access-group icmp-rule in` が付いていること。
2. `show access-lists icmp-rule`
    - deny icmp + time-range の1エントリのみであることを確認。
3. `show time-range blkicmp`
    - 18:01〜23:59 だけが定義済み。

***

## Task 1：West の SSH + AAA 設定

**West**

```
enable
configure terminal
crypto key generate rsa modulus 2048
username westadmin password westadminpass
no aaa authentication login SSH_Connections local none
aaa authentication login SSH_Connections local
line vty 0 4
login authentication SSH_Connections
end
copy run start
```

**解説：**

- `crypto key generate rsa modulus 2048`
    - 2048bit の RSA 鍵を生成し、SSH を有効化。`ip domain-name` は既に設定済みなのでこれだけで良い。[^1]
- `username westadmin password westadminpass`
    - ローカルユーザDBに認証用アカウントを追加。
- `no aaa authentication login SSH_Connections local none`
    - 既存リストから `none` を削除。`none` が残っていると「ユーザ名/パスワードが間違っても認証成功する」経路が残り、要件「認可する」が満たせない。[^1]
- `aaa authentication login SSH_Connections local`
    - 修正したリストを再定義し、ローカルユーザのみを使用。
- `login authentication SSH_Connections`（VTY）
    - VTY で SSH 接続時、このリストを使って認証するようにする。
→ これで SSH ログインすると `Username: westadmin` `Password: westadminpass` のみが有効になる。

***

## Task 2：East の ICMP 制御（9:00〜18:00のみ許可）

**East**

```
enable
configure terminal
time-range blkicmp
periodic daily 0:00 to 8:59
ip access-list extended icmp-rule
permit ip any any
end
copy run start
```

**解説：**

- 既存 time-range blkicmp は `18:01-23:59` のみ。
- ここに `periodic daily 0:00 to 8:59` を追加すると、blkicmp は
    - 0:00〜8:59 と 18:01〜23:59 の二つの時間帯を表す。[^1]
- ACL の既存行：`10 deny icmp any any time-range blkicmp`
    - 上記時間帯は ICMP を deny。
- `permit ip any any` を ACL の末尾に追加
    - これが行番号20として追加される。
    - 結果：
        - 0:00〜8:59,18:01〜23:59 → エントリ10がマッチして ICMP は deny。
        - 9:00〜18:00 → エントリ10は time-range 非アクティブで無視、エントリ20がマッチして全トラフィック permit（ICMP含む）。

denyエントリは追加していないのでタスク条件も守れている。

***

## 検証コマンドと確認ポイント

### West の SSH

1. **設定確認**
```
show running-config | include aaa authentication login
show running-config | section vty
show crypto key mypubkey rsa
```

- `aaa authentication login SSH_Connections local` になっているか。
- line vty に `login authentication SSH_Connections` があるか。
- RSA鍵が 2048bit で生成されているか。

2. **実接続**

- ISP か East など他ルータから

```
ssh -l westadmin 192.168.20.1
```

- 正しいパスワードでログインでき、間違ったユーザ/パスでは拒否されること。


### East の ICMP 制御

1. **time-range と ACL**
```
show time-range
show access-lists icmp-rule
```

- blkicmp に `0:00-8:59` と `18:01-23:59` の2つの periodic が載っているか。
- ACL が
    - `10 deny icmp any any time-range blkicmp`
    - `20 permit ip any any`
になっているか。[^1]

2. **時間帯ごとの挙動（概念的）**

- 実環境では時刻変更が必要だが、試験では基本的に設定と time-range 状態だけ見られればOK。
- 実際にテストするなら（時刻を 10:00 に変更して）
    - West や ISP から East e0/1 宛に `ping 192.168.10.1` → 通る。
- 18:30 に変更すれば ping は失敗するはず。

***

この問題は、

- West：AAAリストから `none` を外して VTY に適用
- East：time-range を「禁止時間帯」にして ACL に1つだけ permit を足す

という2点だけを確実に覚えておくと、本番でも素早く対応できます。

ここまで見て、AAA 関連と ACL+time-range のどちらの方がまだ不安に感じますか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

