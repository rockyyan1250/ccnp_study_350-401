# QUESTION 13もお願い。

Tasks:
Troubleshoot and resolve the issues to achieve these goals:

1. Ensure that R5 can ping the prefix 10.9.99.9. Manipulate the first basic routing decision-making criteria that if a router learns a route from different routing protocols
the admin distance can be changed without using a route-map. Use decimal value of 85 if required to accomplish this.
2. Ensure that R5 loopback 0 reaches to R2's loopback 0 by following the path through R5, R6, R4 to R2 and vice versa. Use metric values K1=100000, K2=1,
K3=255, K4=10, K5=1500 to modify the default metric in EIGRP if required. Do not add or modify the default-metric command under router eigip 10. Do not use a
route-map.
3. Ensure that on R3, prefix 10.0.0.0/8 uses the SP2 to route to the Internet, whereas prefix 172.16.0.0/12 uses the SP1 to route to the Internet. Do not use BGP to
accomplish this. Use the pre-configured route-maps SP1 and SP2 and modify to accomplish the task if required. Use the ping and trace commands from R5 and R1 to
verify results.

QUESTION 13 は内容がかなり濃いので、タスクごとに整理していきます。

***

## Topology 概要

- 左側：OSPF Area 0（R1, R2, R3, R4）
- 右側：EIGRP AS 10（R3, R4, R5, R6）
- 下：RIP（R4–R9）
- 上：SP1, SP2 はインターネット側のプロバイダ。R3 が両方に接続。
- 各ルータの Lo0/Lo1 は 10.n.n.n/24 系（詳細は表参照）。[^1]

R3/R4 は OSPF↔EIGRP↔RIP の再配布ポイントで、ここでの AD や metric の扱いを変えてループを止めたり、経路選択を制御する問題です。[^1]

***

## タスク文の翻訳と意味

1. 「R5 から prefix 10.9.99.9 に ping できるようにしなさい。ルータが複数プロトコルから同じルートを学んだときの『最初の基本的判定基準＝管理距離(AD)』を、route-map を使わずに操作して解決する。必要なら 85 を使うこと。」
→ R9 の Loopback1 (10.9.99.0/24) に対するルーティングループを、R4 の RIP ルートの AD を 85 に下げて OSPF E2 より優先させて止める。[^1]

2. 「R5 の Loopback0 から R2 の Loopback0 への経路（および逆方向）は、R5→R6→R4→R2 を通るべき。必要なら EIGRP のデフォルトメトリック(K1=100000, K2=1, K3=255, K4=10, K5=1500)を使って変更する。ただし router eigrp 10 下の default-metric 行は変更禁止。route-map も使わない。」
→ OSPF→EIGRP への再配布メトリックを R4 だけ高品質（上記 K 値）にし、R3 経由より R4 経由を好むようにする。`match internal` で OSPF内部ルートだけに適用。[^1]

3. 「R3 上で、10.0.0.0/8 のトラフィックは SP2 経由、172.16.0.0/12 のトラフィックは SP1 経由でインターネットに出るようにしなさい。BGP は使わない。事前定義された route-map SP1/SP2 を必要に応じて修正して用いる。結果は R5 と R1 からの ping / traceroute で確認する。」
→ R3 で Policy-Based Routing(PBR) を使い、SP1/SP2 用 route-map に `set ip next-hop` を追加して e0/0 / e0/1 に適用する。[^1]

***

## 作業前に確認すべき設定と理由

1. **R3 の再配布と route-map/SP ACL 設定**
    - `show run | section router eigrp 10`
    - `show run | section router ospf 10`
    - `show run | include route-map SP`
    - 目的：どこで OSPF/EIGRP/static を再配布しているか、SP1/SP2 route-map がどの ACL と紐づいているか（10系/172.16系トラフィックのマッチ条件）を確認。[^1]
2. **R4 の RIP / EIGRP / OSPF 再配布設定**
    - `show run | section router rip`
    - `show run | section router eigrp 10`
    - `show ip route 10.9.99.0`
    - 目的：
        - R9 のルート 10.9.99.0/24 が RIP と OSPF E2 のどちらとして見えているか。
        - ループの原因になっている「RIPルートがOSPF E2に上書きされている」状況を確認。[^1]
3. **R5 から R2 の Lo0 への経路**
    - `show ip route 10.2.2.2` on R5
    - `traceroute 10.2.2.2 source 10.5.5.5 numeric`
    - 目的：現在は R5→R3→R1→R2 と上回り経路を取っていることを確認し、後で R5→R6→R4→R2 に変わったか比較する。[^1]
4. **R3 のデフォルトルートと NAT**
    - `show ip route 0.0.0.0`
    - PBR と組み合わせてインターネット到達性を確保するため、0/0 が Null0 + 再配布されていることを確認。[^1]

***

## 使用LAB

この規模だと General LAB の R1〜R6 に対応させて練習するのが現実的です（R9/ISP は簡略化）。[^2]

***

## Task別 正解コマンドと解説


***

### ✅ Task 3：PBR で 10.0.0.0/8 は SP2、172.16.0.0/12 は SP1 へ（R3）

**R3**

```
enable
configure terminal
route-map SP1 permit 10
set ip next-hop 209.165.201.2
route-map SP2 permit 10
set ip next-hop 209.165.200.226
interface ethernet0/0
ip policy route-map SP1
interface ethernet0/1
ip policy route-map SP2
end
copy run start
```

**解説：**

- 既存の route-map SP1/SP2 はそれぞれ ACL 120/110 による「送信元アドレスマッチ」だけ入っている。（SP1→172.16.0.0/12、SP2→10.0.0.0/8）[^1]
- `set ip next-hop` で、それぞれのトラフィックを送るべき ISP 側の次ホップ（SP1 e0/0, SP2 e0/0）を指定。
    - SP1: 209.165.201.2（R3 e0/2 が .1 なので .2 が SP1）
    - SP2: 209.165.200.226（R3 e0/3 が .225 なので .226 が SP2）[^1]
- `ip policy route-map SP1` を e0/0（172.16.x.x の OSPF 側）に適用し、「このIFから出る 172.16.0.0/12 ソースのトラフィック」を SP1 へ送る。
- `ip policy route-map SP2` を e0/1（10.x.x.x の EIGRP 側）に適用し、「このIFから出る 10.0.0.0/8 ソースのトラフィック」を SP2 へ送る。
- これで BGP なしでソースベースの経路制御が実現できる。

***

### ✅ Task 1：RIP ルートの AD を85にしてループ解消（R4）

**R4**

```
enable
configure terminal
router rip
distance 85 10.0.49.0 0.0.0.255
end
copy run start
```

**解説：**

- R9 の Lo1 (10.9.99.0/24) は RIP で R4 に入るが、R4 は同じネットワークを OSPF External (E2) としても再学習しており、AD 110 の OSPF ルートが AD120の RIP を上書き → 再配布ループが発生。[^1]
- `distance 85 10.0.49.0 0.0.0.255`
    - R9 と接続するネットワーク 10.0.49.0/24 から学習した RIP ルートの AD を 85 に下げる。
    - これにより、同一プレフィックスで OSPF E2 (AD 110) と競合した場合も RIP (AD 85) が選ばれ、ループが止まる。
- ルートは `R 10.9.99.0/24 [85/1] via 10.0.49.9` のように RIP で安定する。[^1]
- その結果、R5 から 10.9.99.9 への traceroute は R5→R6→R4→R9 の3ホップで収束する。

***

### ✅ Task 2：R5↔R2 Lo0 の経路を R5–R6–R4–R2 にする（R4）

**R4**

```
enable
configure terminal
router eigrp 10
no redistribute ospf 10
redistribute ospf 10 match internal metric 100000 1 255 10 1500
end
copy run start
```

**解説：**

- 元々 R3 と R4 は両方 `default-metric 1 1 1 1 1` で OSPF を EIGRP に再配布しており、R5 から見ると「R3の方がASBRに近い」ため R3 経由が選ばれていた。[^1]
- 問題では「K1=100000, K2=1, K3=255, K4=10, K5=1500」を使えとあるので、これを R4 の再配布メトリックとして使用。
- `no redistribute ospf 10` で一旦既存の再配布を消し、
`redistribute ospf 10 match internal metric 100000 1 255 10 1500`
    - OSPF **internal ルートのみ** を新しいメトリックで EIGRP に再配布。
    - R2 の Lo0 などは OSPF internal なので、新しいメトリックが適用され、R4 経由ルートが R3 経由より良くなる。
    - `match internal` を付けることで、R4 が再配布する OSPF default ルートには新メトリックを適用せず、Task3 のインターネット経路選択を壊さない。[^1]
- これで R5 のルーティングは
`D EX 10.2.2.2/32 [170/26368] via 10.0.56.6`
のように、次ホップが R6 → R4 → R2 という経路になる。[^1]

***

## 検証コマンドと確認ポイント

### Task 1 検証（R5からR9 Lo1）

1. **R4 でルート確認**
```
R4# show ip route 10.9.99.0
```

- `R 10.9.99.0/24 [85/1] via 10.0.49.9` となっているか（RIP優先）。[^1]

2. **R5 から traceroute**
```
R5# traceroute 10.9.99.9 numeric
```

- 経路が `10.0.56.6`（R6）→`10.0.46.4`（R4）→`10.0.49.9`（R9）で終了し、ループしないことを確認。


### Task 2 検証（R5 Lo0 ↔ R2 Lo0）

**R5 から R2 Lo0**

```
R5# show ip route 10.2.2.2
R5# traceroute 10.2.2.2 source 10.5.5.5 numeric
```

- ルートの next-hop が `10.0.56.6` になっていること。
- traceroute が `10.0.56.6` (R6) → `10.0.46.4` (R4) → `172.16.24.2` (R2) の順に進むことを確認。[^1]

**逆方向（R2→R5）は元から要件を満たしている**ので、参考として traceroute して同じパスになっていることを見ておく。

### Task 3 検証（PBR）

**R3 からのルートは変えずに、実際の出口だけ変えるので traceroute/ping で確認。**

- R1 (OSPF側) からインターネット宛 1.1.1.1 に ping / traceroute
    - ソースが 172.16.x.x なので SP1 経由になるはず。
- R5 (EIGRP側) から 1.1.1.1 に traceroute
    - ソースが 10.x.x.x なので SP2 経由になるはず。

※試験では実際に SP ルータまでアクセスできない場合もあるので、R3 で

```
show route-map
show ip policy
```

で PBR が正しく適用されているか確認しておくと安心です。

***

この問題で特にややこしいのは「Task2 の metric を internal だけに適用する理由」と「Task1/2/3 が互いに干渉しないように設計されている点」です。

どのタスクのロジックが一番覚えづらそうに感じますか？
<span style="display:none">[^3]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

[^3]: image.jpg

