# QUESTION

Tasks:
Troubleshoot and resolve the issues on West and East routers to achieve these goals:

- ISP should be able to telnet SW2 using preconfigured authentication list and credentials configured locally on SW2. Any modification made to existing ACL must also
include logging for the rule.
- ISP router should only allow traffic sourced from major network 192.168.0.0/16 inbound on its WAN interfaces. Use the preconfigured ACL on ISP router to meet this
requirement and enable logging when new rules are added or existing are modified. Ensure SW2 can ping East Router's e0/0.
You must remove wrong preconfigs that have impact on tasks you are performing to fix issues.
Enable password is 'Cisco' on all devices.
SW2: Local username is "SW2" and password is "Cisco"

QUESTION 20 は、ACL と VTY 設定の組み合わせを直す問題です。

***

## Topology と前提

- ISP と West/East が三角形でつながっていて、SW2 は West の下にぶら下がる。
- SW2 のローカルユーザ: `username SW2 secret Cisco`。
- ISP の e0/0（East側）・e0/1（West側）両方に ACL `ACL` が in で適用されている。[^1]

既存設定（要点）[^1]

- ISP `ip access-list extended ACL`:
    - 10 permit tcp host 192.168.20.2 eq telnet host 20.0.20.1 eq telnet
    - 20 permit ip 192.168.0.0 0.0.255.255 255.255.255.0 0.0.0.255
    - 30 deny ip any any log
- SW2:
    - `aaa new-model`
    - `aaa authentication login TELNET local`
    - line vty 0 4:
        - `transport input ssh`
        - `login authentication TELNET` が未設定（preconfig ではそう）[^1]

***

## タスク文の翻訳と意味

1. 「ISP から SW2 へ telnet できるようにしなさい。SW2 にローカルで設定済みの認証リストと資格情報を使うこと。既存 ACL を修正する場合、そのルールにも logging を含めること。」
→ SW2 の VTY で TELNET を受け入れ、認証リスト TELNET を使う。ISP の ACL で返りトラフィックを許可するが、`log` オプションを付ける。[^1]
2. 「ISP ルータは、WAN インターフェースで 192.168.0.0/16 から来たトラフィックだけを in で許可するようにしなさい。preconfig ACL を使い、新規または修正ルールには logging を有効化する。最後に SW2 から East の e0/0 へ ping が通ること。」
→ ACL の 20番エントリの宛先を `any` に修正し `log` を付ける。これで 192.168.0.0/16 からの全トラフィックを許可し、それ以外は deny ip any any log で落とす。[^1]

***

## Task 1：ISP→SW2 の telnet + 認証

### SW2 側

```
enable
configure terminal
line vty 0 4
transport input ssh telnet
login authentication TELNET
end
copy run start
```

**ポイント**

- `transport input ssh telnet`
    - もともと ssh のみ許可だったので telnet を追加。
- `login authentication TELNET`
    - aaa の `aaa authentication login TELNET local` を VTY に紐付け、ローカルユーザ `SW2 / Cisco` で認証。[^1]


### ISP 側

ACL の 10 番エントリを修正。

```
enable
configure terminal
ip access-list extended ACL
no 10
10 permit tcp host 192.168.20.2 eq telnet host 20.0.20.1 log
end
copy run start
```

**ポイント**

- もともとは `... host 20.0.20.1 eq telnet` と宛先ポートまで telnet を指定していたため、「返ってくる側（ISP）」のランダムポートにはマッチしない。
- 正しくは「ソース 192.168.20.2 の 23番 → 宛先 20.0.20.1（ISP の e0/1）」だけ見たいので、宛先ポート指定は削除。
- ログ要件があるので `log` を追加。[^1]

これで ISP から

```
ISP# telnet 192.168.20.2
Username: SW2
Password: Cisco
```

でログインできる。

***

## Task 2：192.168.0.0/16 以外を WAN で拒否＆ SW2→East ping

ACL 20番を修正。

**ISP**

```
enable
configure terminal
ip access-list extended ACL
no 20
20 permit ip 192.168.0.0 0.0.255.255 any log
end
copy run start
```

**ポイント**

- 元の 20番は `permit ip 192.168.0.0 0.0.255.255 255.255.255.0 0.0.0.255` と宛先もマッチさせており、East/West へのルーティングに合わないため通らないトラフィックが出ていた。[^1]
- 宛先を `any` にすることで、「ソースが 192.168.0.0/16 ならどこ宛でも許可」となり、タスク条件を満たす。
- ここでも `log` 要件を満たすため `log` を付ける。
- ACL 30 の `deny ip any any log` が残るので、それ以外のソースはログ付きで拒否される。

***

## 検証

1. **ISP → SW2 telnet**
```
ISP# telnet 192.168.20.2
```

- ログインに成功し、`SW2#` プロンプトが出ること。
- `show access-lists ACL` で 10番エントリのマッチカウンタが増えていることを確認（ログも見る）。

2. **SW2 → East e0/0 ping**

SW2 から:

```
SW2# ping 192.168.10.1
```

- 成功すること。
- ISP で `show access-lists ACL` を見ると、20番エントリ（192.168.0.0/16）がマッチしているはず。

***

この問題で一番ポイントになるのは、「サーバ側の戻りトラフィックを許可する ACL の書き方（宛先ポートを指定しない）」と、「ソース限定のプレフィックスマッチだけで WAN フィルタを作る」という2点です。

今の説明の中で、ACL の書き方でまだ曖昧な部分はどこでしょうか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

