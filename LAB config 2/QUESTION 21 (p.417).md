# QUESTION 21

Tasks:
Troubleshoot and resolve the issues on West and East routers to achieve these goals:

1. SW2 should only allow telnet access from ISP router's Loopback 0 using the AAA services. Fix the configs on SW2 to achieve this. Use preconfigured access-list
ISP without removing the existing rule.
2. East router is configured to perform forwarding table lookup on an IP packet's source address, and it checks the incoming interface to reduce the risk of IP Address
spoofing. Fix the issue where some East Router fails to ping destinations which are reachable via default route such as loopback 16 on ISP router. Do not advertise
this interface into ospf and neither use a static route on East router to perform this task.
You must remove wrong preconfigs that have impact on tasks you are performing to fix issues.
Enable password is 'Cisco' on all devices
SW2: Local username is "SW2" and password is "Cisco"

QUESTION 21 は、SW2 の VTY ACL と East の uRPF 設定を直す問題です。

***

## Topology と前提

- ISP：Lo0 = 172.16.0.100/32（OSPF area0 で広告）と Lo16 = 172.16.16.16/32（広告しない）。[^1]
- East：
    - e0/0 = 192.168.10.1/24
    - e0/1 = 10.0.10.2/30, `ip verify unicast source reachable-via rx` が設定済み。
    - デフォルトルートは ISP 側に向いている。
- SW2：
    - e0/0 = 192.168.20.2/24
    - ローカルユーザ `SW2 secret Cisco`
    - `aaa authentication login telnet local`
    - 標準ACL `ISP` : `deny any log`
    - line vty 0 4: `access-class ISP in`, `transport input ssh`, `login` 未設定 or そのまま。[^1]

***

## タスクの意図

1. **SW2 への telnet を ISP Lo0 からだけ許可し、AAA 認証を使う。**
    - preconfig ACL `ISP` を使い、「172.16.0.100 だけ permit、それ以外は既存の deny any log」で VTY 制限。
    - VTY で `login authentication telnet` を使ってローカルユーザ SW2/Cisco で認証。[^1]
2. **East で uRPF による source-check が原因で、デフォルトルート経由の宛先（ISP Lo16）への ping が落ちているのを修正。**
    - 既存 `ip verify unicast source reachable-via rx` は「strictモード」で、戻りトラフィックのソース（ISPのループバック16）がデフォルトルート経由では `rx` にマッチしないため drop される。
    - `allow-default` オプションを追加して、デフォルトルートで到達できるソースも許可。[^1]

***

## Task 1：SW2 で ISP Lo0 だけ VTY 許可 + AAA

**SW2**

```
enable
configure terminal
ip access-list standard ISP
5 permit host 172.16.0.100
line vty 0 4
login authentication telnet
end
copy run start
```

**解説：**

- `ip access-list standard ISP` の中に `5 permit host 172.16.0.100` を「追加」する。
    - 既存の `deny any log` はそのまま残るので、結果的に
        - ISP Lo0(172.16.0.100) → permit
        - その他のアドレス → deny any log
    - これを VTY の `access-class ISP in` ですでに適用しているので、VTY に入れるのは ISP Lo0 だけになる。[^1]
- `login authentication telnet`
    - VTY で `aaa authentication login telnet local` を使用。
    - これにより telnet/ssh で入る際にローカルユーザ `SW2 / Cisco` で認証される。

※ telnet 自体を受けたい場合、前の問題と同様に `transport input ssh telnet` が既に設定されているか確認し、必要なら追加。

***

## Task 2：East の uRPF でデフォルトルートを許可

**East**

（解答文では R4 と書かれているが、トポロジ的には East）

```
enable
configure terminal
interface ethernet0/1
ip verify unicast source reachable-via rx allow-default
end
copy run start
```

**解説：**

- 既存：`ip verify unicast source reachable-via rx`
    - strict uRPF。受信パケットのソースIPに対して「FIBで最適経路を引いたときの出力IFが現在の受信IF e0/1 であること」を要求。
    - ISP Lo16(172.16.16.16) は OSPF で広告されておらず、East には「デフォルトルート経由で ISP へ」という 0/0 しかない。
    - strict uRPF はこの default route を通常使わないため、「正当な戻りトラフィック」も不正と判断して drop してしまう。[^1]
- `allow-default` を付けると、FIB 参照時にデフォルトルートで到達できるソースについても OK とみなす。
→ これで East から ISP Lo16 への ping が成功するようになる。

***

## 検証

### SW2 への telnet

1. ISP 上で:
```
ISP# telnet 192.168.20.2
```

- `Username: SW2` / `Password: Cisco` でログインできる。
- 他のルータから同じ操作をすると、ACL `ISP` の deny any log で拒否される。

2. SW2 で:
```
show access-lists ISP
```

- `5 permit host 172.16.0.100` と `10 deny any log` が見えるはず。
- `show line vty 0 4` で `Access list is ISP` と `login Authentication is telnet` を確認。


### East から ISP Lo16 への ping

East から:

```
East# ping 172.16.16.16
```

- 成功すること。
- その際、East の e0/1 で `show ip interface e0/1` を見ると、`IP verify source reachable-via RX, allow-default` となっているはず。

***

この問題のキモは、

- VTY の `access-class` で使う標準ACLを「deny any だけ」から「特定ホスト permit + deny any log」に変えること
- strict uRPF に `allow-default` を付けて default route 経由の正当トラフィックを通すこと

の2点です。

uRPF と ACL のどちらの方が、まだ動きがイメージしにくいですか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

