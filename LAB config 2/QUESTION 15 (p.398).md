# QUESTION 15
Tasks:
Troubleshoot and resolve the issues to achieve these goals:

1. Ensure that R6 can ping the prefix 10.9.99.9. Manipulate the first basic routing decision-making criteria of longest prefix match that if a router learns a route from
different routing protocols, the longest matched prefix can be changed. Use decimal value of 75 if required to accomplish this. Do not use a route-map.
2. Ensure that R2 loopback 1 reaches to R5's loopback 1 by following the path through R2, R4, R6 to R5 and R5 loopback 1 reaches R2's loopback 1 by following the
path through R5, R6, R4 to R2. Use metric values K1= 100000, K2=1, K3=255, K4=10, K5=1500 to modify the default metric in EIGRP if required. Do not add or
modify the default-metric command under router eigrp 10. Do not use a route-map to set metrics.
3. Ensure that on R3, prefix 10.0.56.6/32 uses the SP1 to route to the Internet, whereas prefix 172.16.12.2/32 uses the SP2 to route to the Internet. Do not use BGP to
accomplish this. Use the pre-configured route-maps INTERNET1 and INTERNET2 and modify to accomplish the task if required. Use the ping and trace commands
from R6 and R2 to prefixes 209.165.202.146 and 209.165.202.158, respectively to verify the results.

QUESTION 15 も、QUESTION 13 と同じ構成で「別のパラメータ」をいじるバージョンです。

***

## タスクの直感的な意味

1. **Task 1（R6→10.9.99.9）**
    - R9 の Lo1(10.9.99.0/24) 周りで、RIP と OSPF 再配布によるループが起きている。
    - 今回も R4 で RIP ルートを優先させてループを止めるが、指定値は AD=75。route-map は禁止。[^1]
2. **Task 2（R2 Lo1 ↔ R5 Lo1 の経路）**
    - R2 Lo1(10.2.22.2/24) ↔ R5 Lo1(10.5.55.5/24) の双方向トラフィックを、R2–R4–R6–R5 経由にしたい。
    - 既存設定で R4 の EIGRP 学習ルートが「AD255で無効」にされている＋OSPF/EIGRP 再配布のメトリックが同じなので、R3経由が選ばれている。
    - R4 の `distance 255 ...` を削除し、さらに R4 で OSPF→EIGRP 再配布メトリックを K値（100000,1,255,10,1500）に変えて、R4経由の経路をより優先させる。[^1]
3. **Task 3（特定ホストだけ経路を変える PBR）**
    - R3 上で、
        - 送信元 10.0.56.6/32（R6 のEIGRP側IF）は SP1（209.165.200.236/30 の .237）でインターネットへ
        - 送信元 172.16.12.2/32（R2 の OSPF 側IF）は SP2（209.165.200.228/30 の .229）でインターネットへ
    - 既存の route-map INTERNET1/2 は ACL 110/120 でそれぞれのアドレスをマッチさせるだけになっているので、そこに `set ip next-hop` を追加し、e0/1（EIGRP側）と e0/0（OSPF側）に PBR 適用。[^1]

***

## 事前にどこを見るか（理由付き）

1. **R4 の RIP / EIGRP 設定**
    - `show run | section router rip`
    - `show run | section router eigrp 10`
    - 目的：
        - RIP ルート 10.9.99.0/24 が OSPF E2 に負けている状況を確認。
        - `distance 255 0.0.0.0 255.255.255.255 5` と `redistribute ospf 10 route-map default` があることを把握（Task2対応）。[^1]
2. **R6 から 10.9.99.9 へのループ確認**
    - `traceroute 10.9.99.9 numeric` on R6
    - 目的：ループしている経路を確認し、設定後に短い経路に変わったか比較する。[^1]
3. **R2/R5 から互いの Lo1 への経路**
    - `show ip route 10.5.55.0` on R2
    - `show ip route 10.2.22.0` on R5
    - `traceroute 10.5.55.5 source 10.2.22.2` on R2
    - `traceroute 10.2.22.2 source 10.5.55.5` on R5
    - 目的：現状が R1/R3 経由であることを確認し、後で R4/R6 経由になったかを見る。[^1]
4. **R3 の INTERNET1/2 route-map と ACL**
    - `show run | include INTERNET`
    - `show access-lists 110` / `120`
    - 目的：どの送信元アドレスをマッチしているか（10.0.56.6, 172.16.12.2）と、どのインターフェース向け PBR かを特定。[^1]

***

## Task別 正解コマンドと解説


***

### ✅ Task 1：R6 から 10.9.99.9 に到達させる（R4 の RIP AD を 75 に）

**R4**

```
enable
configure terminal
router rip
distance 75 10.0.49.0 0.0.0.255
end
copy run start
```

**解説：**

- R9 の Lo1(10.9.99.0/24) は RIP で R4 に来ているが、R4 は OSPF E2 も同じプレフィックスで学習し、AD 110 の OSPF で RIP(AD 120) を上書きして再配布ループが発生していた。[^1]
- `distance 75 10.0.49.0 0.0.0.255` により、R9 から学習した RIP ルートだけ AD=75 に変更。
- これで OSPF E2 (AD110) より RIP (AD75) が優先され、R4 の `show ip route 10.9.99.0` は
`R 10.9.99.0/24 [75/1] via 10.0.49.9`
となり、ループが解消される。[^1]

***

### ✅ Task 2：R2 Lo1 ↔ R5 Lo1 の経路を R2–R4–R6–R5 にする（R4）

**R4**

```
enable
configure terminal
router eigrp 10
no distance 255 0.0.0.0 255.255.255.255 5
redistribute ospf 10 route-map default metric 100000 1 255 10 1500
end
copy run start
```

**解説：**

- 既存の `distance 255 0.0.0.0 255.255.255.255 5` は、ACL5 が未定義のため「全ての EIGRP 経路の AD を255(=無効)」としてしまっていた。
    - その結果、R4 は R5/R6 のネットワークを OSPF 再配布からしか知らず、R2 から見た R5/R6 の経路も R3 側の ASBR だけが使われていた。[^1]
- `no distance 255 ...` でこの異常設定を削除し、R4 が R5/R6 への EIGRP インターナルルートを正しくインストールできるようにする。
- 次に `redistribute ospf 10 route-map default metric 100000 1 255 10 1500`
    - OSPF（R2 側）から EIGRP（R5/R6 側）への再配布時に、指定された K値に基づく「良いメトリック」を設定。
    - R3 は依然として `default-metric 1 1 1 1 1` で再配布しているため、R5/R6 から見ると「R4 経由の外部EIGRPルートの方がメトリック的に良い」＝ASBR として R4 が選好される.[^1]
- これにより R2 Lo1 → R5 Lo1 も R5 Lo1 → R2 Lo1 も、
`R2 –(OSPF)→ R4 –(EIGRP)→ R6 –(EIGRP)→ R5` の経路に収束する。

***

### ✅ Task 3：特定ホストに対するインターネット出口を変える PBR（R3）

**R3**

```
enable
configure terminal
route-map INTERNET1 permit 10
set ip next-hop 209.165.200.237
route-map INTERNET2 permit 10
set ip next-hop 209.165.200.229
interface ethernet0/0
ip policy route-map INTERNET2
interface ethernet0/1
ip policy route-map INTERNET1
end
copy run start
```

**解説：**

- 既存の設定：
    - INTERNET1: `match ip address 110` → ACL110 は `permit host 10.0.56.6`（R6 の 10.0.56.6）。
    - INTERNET2: `match ip address 120` → ACL120 は `permit host 172.16.12.2`（R2 の 172.16.12.2）。[^1]
- `set ip next-hop 209.165.200.237`
    - ネットワーク 209.165.200.236/30 で R3 e0/2 は .238 を使用しているので、SP1 e0/0 のIPは .237。
    - これを INTERNET1 に設定することで、「送信元10.0.56.6のトラフィックは SP1 経由」に。
- `set ip next-hop 209.165.200.229`
    - ネットワーク 209.165.200.228/30 で R3 e0/3 が .230、残りの .229 が SP2 e0/0。
    - INTERNET2 に設定し、「送信元172.16.12.2のトラフィックは SP2 経由」に。[^1]
- `ip policy route-map INTERNET2` を e0/0（OSPF側）、`ip policy route-map INTERNET1` を e0/1（EIGRP側）に適用。
    - これで R2 側から来るトラフィックには INTERNET2、R6 側から来るトラフィックには INTERNET1 の PBR が適用される。

***

## 検証コマンドと確認ポイント

### Task 1：R6 から 10.9.99.9

1. R4 でルート確認
```
R4# show ip route 10.9.99.0
```

- `R 10.9.99.0/24 [75/1] via 10.0.49.9` になっていること。[^1]

2. R6 から traceroute
```
R6# traceroute 10.9.99.9 numeric
```

- 経路が `10.0.46.4` (R4) → `10.0.49.9` (R9) で終了し、ループしないこと。


### Task 2：R2 Lo1 ↔ R5 Lo1

**R2 → R5**

```
R2# show ip route 10.5.55.0
R2# traceroute 10.5.55.5 source 10.2.22.2 numeric
```

- ルートの next-hop が `172.16.24.4` (R4)になっている。
- traceroute が `172.16.24.4` → `10.0.46.6`(R6) → `10.0.56.5`(R5) となることを確認。[^1]

**R5 → R2**

```
R5# show ip route 10.2.22.0
R5# traceroute 10.2.22.2 source 10.5.55.5 numeric
```

- next-hop が `10.0.56.6` (R6)、経路が `10.0.56.6` → `10.0.46.4` → `172.16.24.2` になることを確認。


### Task 3：PBR によるインターネット出口

**R6 から SP1 宛へのトラフィック**

```
R6# ping 209.165.202.146 source 10.0.56.6
R6# traceroute 209.165.202.146 source 10.0.56.6 numeric
```

- R6→R5/R4→R3 と進み、R3 からの出口が SP1 (e0/2) 側になっているかを確認。

**R2 から SP2 宛へのトラフィック**

```
R2# ping 209.165.202.158 source 172.16.12.2
R2# traceroute 209.165.202.158 source 172.16.12.2 numeric
```

- R2→R1→R3 と進んだ後、R3 から SP2 (e0/3) 側に出ているかを確認。

***

この問題は QUESTION 13 とかなり似ていますが、

- Task1 の AD が 75、
- Task2 で `distance 255` を消すこと、
- Task3 で route-map 名や next-hop のサブネットが違うこと
が主な差分です。

ここまでで、「どのタスクが一番混乱しやすいか」「どの部分を図に描きながら整理したいか」を教えてもらえますか？

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

