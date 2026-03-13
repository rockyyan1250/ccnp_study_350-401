

# QUESTION 4
続いてQUESTION 4の解説もお願いします。

Tasks:
A company is connected to an ISP and some of the networks between the ISP and the company are not reachable. Troubleshoot and resolve the issues to achieve
these goals:

1. A single /16 is advertised for all infrastructure-connected interfaces that belong to the 10.20.x.x network using BGP network commands from border routers
connected to the ISP. Configuration modification is allowed in R4 and R5 to achieve the results. Do not use the BGP aggregate command.
2. R6 receives the ISP R2 Loopback2 from R4 and receives a summary address for both Loopbacks of ISP R2 from R4 or R5. Use BGP attribute local-preference,
add <default value + router number>, for example, for R6, use "default+6 = value to be used". Use the existing prefix lists or route maps with the sequence numbering
starting at 10 and added in increments of 10.
3. R6 receives the ISP R2 Loopback1 from R5 and receives a summary address for both Loopbacks of ISP R2 from R4 or R5 using the same guidelines.
4. R6 advertises its Loopback1 /24 address through BGP.

QUESTION 4 について、これまでと同じスタイルで整理します。

***

## Topology 解説

- 上側：ISP AS 65001
    - R1, R2, R3 が ISP 側
    - R2 Loopback1: 192.168.2.2/24
    - R2 Loopback2: 192.168.3.2/24
    - R1–R2–R3 間は 10.10.12.0/24, 10.10.23.0/24, 10.10.13.0/24 などで接続
- 下側：Company AS 65000
    - R4, R5 が ISP との境界ルータ（それぞれ R1, R3 に接続）
    - R6 は社内コアルータ
    - 10.20.45.0/24, 10.20.56.0/24 など 10.20.x.0/24 が社内インフラ
    - R6 Loopback1: 172.16.6.6/24

R4・R5 が「会社側からISPへBGPピアリングしているボーダー」，R6 が社内の中心で、R6 から見て ISP のループバック（192.168.2.2/24, 192.168.3.2/24）とそのサマリに正しく到達できるようにする問題です。[^1]

***

## タスク文の翻訳と意味

1. 「10.20.x.x ネットワークに属するすべてのインフラ接続インターフェースを、/16 の単一プレフィックス（10.20.0.0/16）として ISP へ広告すること。BGP の network コマンドを境界ルータ（R4, R5）で用いて実現せよ。aggregate コマンドは禁止。」
→ BGP の `network 10.20.0.0 mask 255.255.0.0` はすでにあるが、IGP に 10.20.0.0/16 のルートがないため広告されていない。R4 と R5 で 10.20.0.0/16 のスタティックルートを作り、BGP がマッチできるようにする。[^1]

2. 「R6 は ISP R2 の Loopback2（192.168.3.0/24）を R4 から受信し、さらに R4 または R5 のどちらかから R2 の両方のループバックをまとめたサマリアドレス（192.168.2.0/23）を受信すること。local-preference を『デフォルト値＋ルータ番号』で設定する。既存の prefix-list/route-map を使い、seq は 10 から 10刻み。」
→ R4 は 192.168.3.0/24 をインバウンドで許可し、R4 と R5 両方で aggregate-address 192.168.2.0/23 を設定、local-pref を R4=104 にする。[^1]

3. 「R6 は ISP R2 の Loopback1（192.168.2.0/24）を R5 から受信し、サマリ 192.168.2.0/23 も R4 または R5 から受信すること。同じガイドラインに従うこと。」
→ R5 は 192.168.2.0/24 をインバウンドで許可し、local-pref を 105 にする。[^1]

4. 「R6 は自分の Loopback1（172.16.6.6/24）を BGP で広告すること。」
→ `network 172.16.6.0 mask 255.255.255.0` を設定する。既存の `network 172.16.6.0`（クラスフル）は削除。[^1]

***

## 事前に確認すべき設定と理由

本番試験では、設定に入る前に以下を確認します。

1. **R4/R5 の BGP 設定**
    - `show run | section bgp`
    - 目的：
        - AS 番号が 65000 であること
        - `network 10.20.0.0 mask 255.255.0.0` が既にあること
        - `neighbor ... route-map AS65001-in in` の存在と、route-map / prefix-list の中身を確認するため。[^1]
2. **R4/R5 の prefix-list / route-map**
    - `show run | include AS65001-in`
    - 目的：
        - 192.168.2.0/24 と 192.168.3.0/24 のどちらを deny しているか確認
        - route-map が `deny 10` のみで、全ルートを落としていることを把握する。[^1]
3. **R6 の BGP network 設定**
    - `show run | section bgp`（R6）
    - 目的：
        - `network 172.16.6.0` が mask なしで設定されていることを確認し、Task4 で修正対象だと理解する。[^1]
4. **IGP ルートの有無**
    - `show ip route 10.20.0.0`（R4/R5）
    - 目的：
        - 10.20.0.0/16 が存在しないため BGP が広告できていないことを確認する。[^1]

***

## 使用するLAB

このBGPトポロジはルータ 4〜6 台を使うので、**General LAB** が最も近いです。

- R2,R3,R4,R5,R6 を General LAB の R2〜R6 に対応させて再現する形で練習できます。[^2]

***

## Pre-setting（事前設定コマンド）

ここでは問題文の状態を再現するための最低限の例を示します（実ラボでは既に入っている想定）。

### R4

```
enable
configure terminal
hostname R4
interface loopback 0
 ip address 10.20.4.4 255.255.255.255
interface gigabitEthernet 0/1
 ip address 10.20.45.4 255.255.255.0
 no shutdown
interface gigabitEthernet 0/0
 ip address 10.41.14.2 255.255.255.248
 no shutdown
router bgp 65000
 bgp log-neighbor-changes
 neighbor 10.41.14.1 remote-as 65001
 neighbor 10.20.45.5 remote-as 65000
 address-family ipv4
  network 10.20.0.0 mask 255.255.0.0
  neighbor 10.41.14.1 activate
  neighbor 10.41.14.1 route-map AS65001-in in
  neighbor 10.20.45.5 activate
 exit-address-family
ip prefix-list AS65001-in seq 10 deny 192.168.2.0/24
route-map AS65001-in deny 10
 match ip address prefix-list AS65001-in
end
copy run start
```


### R5

```
enable
configure terminal
hostname R5
interface loopback 0
 ip address 10.20.5.5 255.255.255.255
interface gigabitEthernet 0/1
 ip address 10.20.45.5 255.255.255.0
 no shutdown
interface gigabitEthernet 0/0
 ip address 10.53.35.4 255.255.255.248
 no shutdown
interface gigabitEthernet 0/2
 ip address 10.20.56.5 255.255.255.0
 no shutdown
router bgp 65000
 bgp log-neighbor-changes
 neighbor 10.53.35.3 remote-as 65001
 neighbor 10.20.45.4 remote-as 65000
 neighbor 10.20.56.6 remote-as 65000
 address-family ipv4
  network 10.20.0.0 mask 255.255.0.0
  neighbor 10.53.35.3 activate
  neighbor 10.53.35.3 route-map AS65001-in in
  neighbor 10.20.45.4 activate
  neighbor 10.20.56.6 activate
 exit-address-family
ip prefix-list AS65001-in seq 10 deny 192.168.3.0/24
route-map AS65001-in deny 10
 match ip address prefix-list AS65001-in
end
copy run start
```


### R6

```
enable
configure terminal
hostname R6
interface loopback 1
 ip address 172.16.6.6 255.255.255.0
interface gigabitEthernet 0/3
 ip address 10.20.56.6 255.255.255.0
 no shutdown
router bgp 65000
 bgp log-neighbor-changes
 neighbor 10.20.56.5 remote-as 65000
 address-family ipv4
  network 172.16.6.0
  neighbor 10.20.56.5 activate
 exit-address-family
end
copy run start
```


***

## Task別 正解コマンドと解説


***

### ✅ Task 1：10.20.0.0/16 を広告できるようにする

**R4**

```
enable
configure terminal
ip route 10.20.0.0 255.255.0.0 null0
end
copy run start
```

**R5**

```
enable
configure terminal
ip route 10.20.0.0 255.255.0.0 null0
end
copy run start
```

**解説：**

- BGP の `network 10.20.0.0 mask 255.255.0.0` は「RIB に10.20.0.0/16が存在する場合に限り広告する」という意味。
- もともと存在しているのは各インターフェースの /24 ルートのみ（10.20.45.0/24, 10.20.56.0/24 など）で /16 は無いので、BGP は広告していなかった。[^1]
- `ip route 10.20.0.0 255.255.0.0 null0` を入れることで R4/R5 の RIB に /16 が追加され、BGP が /16 をISPに広告できるようになる。
- 宛先不明の 10.20.x.x へのトラフィックは `null0` に破棄されるが、サマリ広告の典型的な手法。

***

### ✅ Task 2 \& 3：R4/R5でR2のLoopbackを制御し、local-prefを設定

#### R4

```
enable
configure terminal
ip prefix-list AS65001-in seq 20 permit 192.168.3.0/24
router bgp 65000
bgp default local-preference 104
address-family ipv4
aggregate-address 192.168.2.0 255.255.254.0
no route-map AS65001-in
route-map AS65001-in permit 10
match ip address prefix-list AS65001-in
end
copy run start
```


#### R5

```
enable
configure terminal
ip prefix-list AS65001-in seq 20 permit 192.168.2.0/24
router bgp 65000
bgp default local-preference 105
address-family ipv4
aggregate-address 192.168.2.0 255.255.254.0
no route-map AS65001-in
route-map AS65001-in permit 10
match ip address prefix-list AS65001-in
end
copy run start
```

**解説（R4側）：**

1. `ip prefix-list AS65001-in seq 20 permit 192.168.3.0/24`
    - 既存の `seq 10 deny 192.168.2.0/24` に続けて、Loopback2（192.168.3.0/24）だけを許可。
    - これにより、Loopback1 は deny、Loopback2 は permit という状態になる。[^1]
2. `bgp default local-preference 104`
    - AS65000内でR4が学習したルートの local-pref をデフォルトより少し高い 104 に設定（「デフォルト＋ルータ番号」）。
    - これにより R6 から見たときに、R4 経由の経路は local-pref 104 が付与される。
3. `aggregate-address 192.168.2.0 255.255.254.0`
    - R4 が受信した 192.168.3.0/24（と、R2から届く192.168.2.0/24があれば）を `192.168.2.0/23` として要約広告。
    - これが「両ループバックのサマリアドレス」として R6 に届く。[^1]
4. `no route-map AS65001-in` → `route-map AS65001-in permit 10`
    - もともとの route-map は `deny 10` だけだったため、AS65001からの全ルートを拒否していた。
    - いったん削除 (`no route-map`) してから `permit 10` に作り直し、先ほどの prefix-list で許可された 192.168.3.0/24 だけを受け入れるようにする。[^1]

**解説（R5側）：**

- R5 では逆に 192.168.2.0/24 を受け入れ、192.168.3.0/24 を拒否する。
- local-pref は 105（デフォルト+5）にし、R5 経由の経路を R4 より少し優先させる。
- 同じく aggregate-address 192.168.2.0/23 を設定し、R4 と同様にサマリも広告する。[^1]

結果として：

- R6 は
    - Loopback2（192.168.3.0/24）を R4 経由で受信
    - Loopback1（192.168.2.0/24）を R5 経由で受信
    - サマリ 192.168.2.0/23 を R4 または R5 どちらか（あるいは両方）から受信
- local-pref により、R6 は要求どおりの経路選択を行う。

***

### ✅ Task 4：R6 の Loopback1 を /24 として広告

**R6**

```
enable
configure terminal
router bgp 65000
address-family ipv4
no network 172.16.6.0
network 172.16.6.0 mask 255.255.255.0
end
copy run start
```

**解説：**

- 既存の `network 172.16.6.0` はクラスフル（/16）扱いで、実際の IF は 172.16.6.6/24 なのでマッチしない。
- 一度削除してから `mask 255.255.255.0` を付けて再設定すると、`172.16.6.0/24` がRIBに存在するため、BGP はこの /24 を広告する。[^1]

***

## 検証コマンドと確認ポイント

### 1. 10.20.0.0/16 の広告確認

**R4/R5**

```
show ip route 10.20.0.0
show ip bgp 10.20.0.0
```

- RIB に `S 10.20.0.0/16 [1/0] via Null0` があることを確認。
- `show ip bgp 10.20.0.0` で BGP に /16 エントリが存在し、`*>`でマークされていれば ISP へ広告されている。


### 2. ISPルートの受信とフィルタ確認（R4/R5）

```
show ip bgp 192.168.2.0
show ip bgp 192.168.3.0
show ip prefix-list AS65001-in
show route-map AS65001-in
```

- R4 では `192.168.3.0/24` だけが受信され `192.168.2.0/24` が存在しないこと。
- R5 ではその逆になっていることを確認。
- prefix-list の `seq 10 deny` / `seq 20 permit` の内容が期待どおりになっているかを見る。


### 3. サマリルートと local-pref の確認（R6）

```
show ip bgp 192.168.2.0
show ip bgp 192.168.3.0
show ip bgp 192.168.2.0 255.255.254.0
```

- `192.168.2.0/24` のエントリの `LocalPref` が 105 で、`192.168.3.0/24` の LocalPref が 104 になっているか確認。
- `192.168.2.0/23` のサマリエントリが存在するかも確認する。


### 4. R6 の Loopback 広告確認

```
show ip bgp 172.16.6.0
show ip route 172.16.6.0
```

- `show ip bgp` で `172.16.6.0/24` が `*>` として自AS 65000 から広告されていること。
- `show ip route` で `L 172.16.6.0/24` が Loopback1 に紐づいていること。

***

## 本番でのポイント

- まず `show run | section bgp` と `show run | include AS65001-in` を見て「どのルートが deny されているか」を必ず確認する。
- aggregate コマンド禁止と書いてある Task1 と違い、Task2/3 では aggregate-address を使う指示がある点を読み違えない。
- local-pref は **default + router番号** というヒントを見逃さない（R4=104, R5=105）。
- 変更後は `clear ip bgp *` が必要な場合もあるので、試験の指示に応じて実行する。[^1]

次のシミュレーション問題も、同じフォーマットで解説していきます。次にやりたいQUESTION番号を教えてください。
<span style="display:none">[^3]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

[^3]: image.jpg

