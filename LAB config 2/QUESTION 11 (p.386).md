# QUESTION 11

asks:
HUB and SPOKE routers are configured using mGRE tunnels according to the topology. Configure HUB and SPOKE routers to achieve these goals:

1. Configure NHRP authentication using password "Ci\$c0123".
2. Configure SPOKE routers to establish direct tunnels between them where LAN routes should be learned from the tunnel interfaces.

QUESTION 11 についてまとめます。

***

## Topology と前提

- R0：Hub（Tunnel0=10.0.0.254/24, mGRE）
- R1：Spoke1（Tunnel0=10.0.0.1/24, LAN=10.100.1.0/24）
- R2：Spoke2（Tunnel0=10.0.0.2/24, LAN=10.100.2.0/24）
- ルータ間の 192.168.1.x/30 はWAN物理リンク。
- 既に NHRP / OSPF は設定済みで、Hub–Spoke 間の到達性はある状態。[^1]

***

## タスク文の翻訳と意味

1. 「NHRP 認証をパスワード `Ci$c0123` で設定せよ。」
→ Hub と 2 つの Spoke すべての Tunnel0 に同じ `ip nhrp authentication` を入れる。1台だけだと NHRP 登録が失敗する。[^1]
2. 「Spoke ルータ同士が **直接トンネル** を張れるようにしなさい。LANルートはトンネルインターフェースから学習されること。」
→ 今は Spoke のトンネルが `tunnel destination 192.168.1.2` で「Hub固定」の Point-to-Point GRE（DMVPN phase1）なので、**Hub経由でしか通信できない**。
→ Spoke から `tunnel destination` を削除し、`tunnel mode gre multipoint` に変更して mGRE にすれば、NHRP を使った Spoke-to-Spoke トンネル（DMVPN phase2）が張れる。[^1]

***

## 作業前に確認すべき設定と理由

各ルータで以下を確認します。

1. `show run | section Tunnel0`
    - R0 は既に `tunnel mode gre multipoint`、R1/R2 は `tunnel destination` ありで point-to-point になっていることを確認。
    - NHRP 設定（`ip nhrp map` / `ip nhrp nhs` / `ip nhrp network-id`）がすでに正しいことも見る。[^1]
2. `show ip route ospf`
    - 現時点でも R1/R2 から他の LAN（10.100.0.0/24, 10.100.2.0/24 など）へ OSPF ルートが Tunnel0 経由で見えていることをチェック。
    - Spoke-to-Spoke トンネル導入後も OSPF で LAN ルートが Tunnel0 から学習されるか比較する。[^1]
3. `traceroute 10.100.2.1`（R1 から）
    - まだ Spoke-to-Spoke になっていないので、初回は R0 を経由する経路（10.0.0.254 → 10.0.0.2）であることを確認しておく。[^1]

***

## 使用LAB

これも 3 ルータ構成なので、前の DMVPN 問題と同じく **CSR LAB or General LAB** を利用できます。[^2]

***

## Pre-setting（事前設定コマンド）

問題文に記載されている既存コンフィグを再現した例です（本番ではすでに入っている想定）。

### R0（Hub）

```
enable
configure terminal
hostname R0
interface tunnel 0
 ip address 10.0.0.254 255.255.255.0
 no ip redirects
 ip nhrp network-id 10
 ip ospf network broadcast
 ip ospf priority 255
 tunnel source 192.168.1.2
 tunnel mode gre multipoint
interface ethernet0/0
 ip address 192.168.1.2 255.255.255.252
interface ethernet0/1
 ip address 10.100.0.1 255.255.255.0
router ospf 1
 network 10.0.0.0 0.255.255.255 area 0
ip route 192.168.1.4 255.255.255.252 192.168.1.1
ip route 192.168.1.8 255.255.255.252 192.168.1.1
end
copy run start
```


### R1（Spoke1）

```
enable
configure terminal
hostname R1
interface tunnel 0
 ip address 10.0.0.1 255.255.255.0
 ip nhrp map multicast 192.168.1.2
 ip nhrp map 10.0.0.254 192.168.1.2
 ip nhrp network-id 10
 ip nhrp nhs 10.0.0.254
 ip ospf network broadcast
 ip ospf priority 0
 tunnel source 192.168.1.6
 tunnel destination 192.168.1.2
interface ethernet0/0
 ip address 192.168.1.6 255.255.255.252
interface ethernet0/1
 ip address 10.100.1.1 255.255.255.0
router ospf 1
 network 10.0.0.0 0.255.255.255 area 0
ip route 192.168.1.0 255.255.255.252 192.168.1.5
ip route 192.168.1.8 255.255.255.252 192.168.1.5
end
copy run start
```


### R2（Spoke2）

```
enable
configure terminal
hostname R2
interface tunnel 0
 ip address 10.0.0.2 255.255.255.0
 ip nhrp map multicast 192.168.1.2
 ip nhrp map 10.0.0.254 192.168.1.2
 ip nhrp network-id 10
 ip nhrp nhs 10.0.0.254
 ip ospf network broadcast
 ip ospf priority 0
 tunnel source 192.168.1.10
 tunnel destination 192.168.1.2
interface ethernet0/0
 ip address 192.168.1.10 255.255.255.252
interface ethernet0/1
 ip address 10.100.2.1 255.255.255.0
router ospf 1
 network 10.0.0.0 0.255.255.255 area 0
ip route 192.168.1.0 255.255.255.252 192.168.1.9
ip route 192.168.1.4 255.255.255.252 192.168.1.9
end
copy run start
```


***

## Task別 正解コマンドと解説


***

### ✅ Task 1：NHRP 認証の設定

**R0**

```
enable
configure terminal
interface tunnel 0
ip nhrp authentication Ci$c0123
end
copy run start
```

**R1**

```
enable
configure terminal
interface tunnel 0
ip nhrp authentication Ci$c0123
end
copy run start
```

**R2**

```
enable
configure terminal
interface tunnel 0
ip nhrp authentication Ci$c0123
end
copy run start
```

**解説：**

- `ip nhrp authentication Ci$c0123`
    - NHRP のリクエスト/レスポンスに共通パスワードを付与し、NHS とクライアントが一致したパスワードを持つことを要求。
    - 3台すべてに設定しないと、NHRP 登録が失敗し、数分後に NHRP エントリが消えてトラフィックが通らなくなる。[^1]

***

### ✅ Task 2：Spoke同士の直接トンネル（DMVPN Phase2）

**R1**

```
enable
configure terminal
interface tunnel 0
no tunnel destination
tunnel mode gre multipoint
end
copy run start
```

**R2**

```
enable
configure terminal
interface tunnel 0
no tunnel destination
tunnel mode gre multipoint
end
copy run start
```

**解説：**

- `no tunnel destination`
    - それまで「Hub の IP へ固定」だった GRE トンネルの宛先を削除し、動的に多対多で張れるようにする。
- `tunnel mode gre multipoint`
    - Spoke 側 Tunnel0 を mGRE に変更。NHRP を使って他 Spoke の NBMA アドレスを解決し、**Spoke-to-Spoke トンネル**を自動生成できるようになる。[^1]

既に R0 は mGRE + `ip ospf priority 255` になっており、R1/R2 は `ip ospf priority 0` が設定済みなので、DMVPN Phase2 に必要な追加コマンドはこれだけでよい。

***

## 検証コマンドと確認ポイント

### 1. NHRP 登録確認

**R1/R2:**

```
show ip nhrp
```

- HUB (10.0.0.254) や相手 Spoke の Tunnel IP (10.0.0.2 / 10.0.0.1) のエントリが表示されるか。
- Spoke-to-Spoke トンネル確立後は、相手 Spoke のエントリが `dynamic` で追加される。


### 2. OSPF ルート確認

**R1で：**

```
show ip route ospf
```

- 10.100.0.0/24 と 10.100.2.0/24 のルートが Tunnel0 経由で存在することを確認。
- これは「LAN routes should be learned from the tunnel interfaces」を満たしているかの確認でもある。[^1]


### 3. Spoke-to-Spoke トンネルの経路確認（traceroute）

**変更前（確認用）：**

```
R1# traceroute 10.100.2.1 numeric
```

- 1ホップ目 10.0.0.254 (R0)、2ホップ目 10.0.0.2 (R2) と表示され、Hub 経由であることを確認。[^1]

**変更後（Phase2 有効後）：**

同じコマンドを2回実行する。

1回目：

```
R1# traceroute 10.100.2.1 numeric
```

- 初回はまだ情報が無いため Hub を経由するが、この通信が NHRP 解決のきっかけとなり Spoke-to-Spoke トンネルが張られる。

2回目：

```
R1# traceroute 10.100.2.1 numeric
```

- 1ホップ目が `10.0.0.2`（R2 の Tunnel IP）のみになれば、Spoke-to-Spoke トンネルが直接使われている証拠。[^1]


### 4. PC 間の疎通

PC1/PC2/PC3 を模したホストからお互いに ping して、エンドツーエンド接続を確認する。

***

この問題で押さえるべきキーワードは「`ip nhrp authentication` は全台」「Spoke の `no tunnel destination` + `tunnel mode gre multipoint` で Phase2」という2点です。

ここまでで DMVPN Phase1 ↔ Phase2 の違いについて、まだ整理したいポイントはありますか？
<span style="display:none">[^3]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image-2.jpg

[^3]: image.jpg

