# QUESTION 22もお願いします。

Tasks:
Troubleshoot and resolve the issues to achieve these goals:

1. Ensure that R1 reaches the prefix 10.6.66.6 without any single point of failure in the path through R3 or R4 if R4 or R3 are not available for any reason. Do not use a
static route or policy-based routing to accomplish this.
2. Ensure that R1 loopback 1 reaches R6's loopback 1 by following the path through R1, R3, R5 to R6 and vice versa through R6, R5, R3 to R1. Use metric values
K1=10000, K2=1, K3=255, K4=10, and K5=1500 when redistributing OSPF into EIGRP. Do not use a route-map.
3. Ensure that on R3, prefix 10.0.56.6/32 uses the SP1 to route to the Internet, whereas prefix 172.16.12.2/32 uses the SP2 to route to the Internet. Do not use BGP or
static route to accomplish this. Use the pre-configured route-maps SP1 and SP2 and modify to accomplish the task if required. Use the extended ping and trace
commands from R6 and R2 to prefixes 209.165.202.132 and 209.165.202.128, respectively to verify the results.

QUESTION 22 のポイントをタスク別に整理します。

***

## 事前状況のざっくり整理

- 左側 OSPF Area 0（R1, R2, R3, R4）。
- 右側 EIGRP AS 10（R3, R4, R5, R6）。
- 下に RIP（R4–R9）。
- ISP 側は今回も SP1 / SP2 で R3 が 2本のインターネット回線を持つ。[^1]

既存の「おかしい」設定（抜粋）[^1]

- R3/R4 の EIGRP には

```
router eigrp 10
 distance 255 0.0.0.0 255.255.255.255 66
!
access-list 66 permit 10.6.66.0
```

→ 10.6.66.0/24 に対して「AD=255 = 到達不可」にしてしまう。
- R3 の EIGRP

```
redistribute ospf 10
default-metric 1 1 1 1 1
```

→ OSPF→EIGRP 再配布時のメトリックが R4 と同じなので、R6 Lo1 への返りトラフィックでどちらの ASBR（R3 or R4）を通るか制御できていない。
- R3 の route-map SP1/SP2 は `match ip address 110/120` だけで `set ip next-hop` が未設定。[^1]

***

## Task 1：R1 から 10.6.66.6 への経路に単一点障害がないようにする

**狙い**

- R1 が 10.6.66.6（R6 Lo1）に行くとき、R3 経由と R4 経由の2経路を持ちたい。
- しかし現在は R3/R4 の EIGRP で `distance 255 ... 66` のせいで 10.6.66.0/24 の EIGRP ルート自体が「無効」となっている。[^1]

**修正コマンド**

R3:

```plaintext
enable
configure terminal
router eigrp 10
no distance 255 0.0.0.0 255.255.255.255 66
end
copy run start
```

R4:

```plaintext
enable
configure terminal
router eigrp 10
no distance 255 0.0.0.0 255.255.255.255 66
end
copy run start
```

**結果イメージ**

- R1 の `show ip route 10.6.66.6` で、OSPF が再配布した経路として、R3/R4 どちらか（あるいは両方）のパスが入り、どちらか片方が落ちてももう一方で到達可能になる。[^1]

***

## Task 2：R1 Lo1 ↔ R6 Lo1 を R1–R3–R5–R6 経由にする

**狙い**

- デフォルトでは、R6 ロ1 → R1 ロ1 の戻り経路が、距離/メトリック次第で R4 側に逃げる可能性がある。
- 指定された K値（`10000 1 255 10 1500`）を、OSPF→EIGRP 再配布に使って R3 でだけ「より良い外部メトリック」にして、ASBR として R3 を選ばせる。[^1]

**修正コマンド（R3）**

```plaintext
enable
configure terminal
router eigrp 10
redistribute ospf 10 metric 10000 1 255 10 1500
end
copy run start
```

※ 既存の `redistribute ospf 10` を上書きする形になる。

**動作イメージ**

- R6 から見ると、R1 Lo1(10.1.xx.xx)への外部EIGRPルートは
    - R3 が再配布したもの：メトリック = (10000,1,255,10,1500)
    - R4 が再配布したもの：`default-metric 1 1 1 1 1` ベース
- より良いメトリックの R3 経由を選ぶため、
    - R6 Lo1 → R1 Lo1: R6–R5–R3–R1
    - R1 Lo1 → R6 Lo1: OSPF経由で R3 に入り、そこから EIGRP で R5–R6 へ
というパスになる。[^1]

***

## Task 3：特定ホストに対するインターネット出口を PBR で制御

**要件**

- R3 で
    - 送信元 10.0.56.6/32（R6 のインターフェース）は SP1 経由（209.165.201.0/30 側）
    - 送信元 172.16.12.2/32（R2 のインターフェース）は SP2 経由（209.165.200.224/30 側）
- 既存の route-map:
    - SP1 → ACL110（10.0.56.6 を含む 10.0.0.0/8 トラフィック）
    - SP2 → ACL120（172.16.12.2 を含む 172.16.0.0/12 トラフィック）[^1]

**修正コマンド（R3）**

```plaintext
enable
configure terminal
route-map SP1 permit 10
 set ip next-hop 209.165.201.2
route-map SP2 permit 10
 set ip next-hop 209.165.200.226
interface ethernet0/0
 ip policy route-map SP2
interface ethernet0/1
 ip policy route-map SP1
end
copy run start
```

**ポイント**

- `209.165.201.2`：ネットワーク 209.165.201.0/30 で、R3 e0/2 が .1 なので SP1 e0/0 が .2。
- `209.165.200.226`：ネットワーク 209.165.200.224/30 で、R3 e0/3 が .225 なので SP2 e0/0 が .226。[^1]
- e0/0 は OSPF 側（172.16.13.0/29）、e0/1 は EIGRP 側（10.0.35.0/29）に接続しているため、
    - OSPF 側から来るトラフィックに SP2 用 PBR
    - EIGRP 側から来るトラフィックに SP1 用 PBR
を適用することで、指定されたソースごとに出口を変えられる。

**検証イメージ**

- R6 から `extended ping` / `traceroute 209.165.202.132 source 10.0.56.6` を実行 → R3 で SP1 側へ出る。
- R2 から `extended ping` / `traceroute 209.165.202.128 source 172.16.12.2` を実行 → R3 で SP2 側へ出る。[^1]

***

## まとめ

必要な修正は次の4つだけです。

- R3: `no distance 255 ... 66`
- R4: `no distance 255 ... 66`
- R3: `redistribute ospf 10 metric 10000 1 255 10 1500`
- R3: PBR 用 route-map SP1/SP2 に `set ip next-hop` を入れて e0/0,e0/1 にポリシ適用

このうち一番イメージが付きづらいのは、AD 255 を外す話・EIGRP メトリック調整・PBR のどれでしょうか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

