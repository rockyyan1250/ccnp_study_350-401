# QUESTION 2

Tasks:
A DMVPN network is preconfigured with tunnel 0 IP address 192.168.1.254 on the HUB, IP connectivity, crypto policies, profiles, and EIGRP AS 100. The NHRP
password is ccnp123, and the network ID and tunnel key is EIGRP ASN. Do not introduce a static route. Configure DMVPN connectivity between routers BR1 and
BR2 to the HUB router using physical interface as the tunnel source to achieve these goals:

1. Configure NHRP authentication, static IP-to-NBMA address maps, hold time 5 minutes, network ID, and server on branch router BR1.
2. Configure NHRP authentication, static IP-to-NBMA address maps, hold time 5 minutes, network ID, and server on branch router BR2.
3. Ensure that packet fragmentation is done before encryption to account for GRE and IPsec header and allow a maximum TCP segment size of 1360 on an IP MTU
of 1400 on the tunnel interfaces of both branch routers.
4. Apply an IPsec profile to the tunnel. Verify that direct spoke-to-spoke tunnel is functional between branch routers BR1 and BR2 by using traceroute to Ethernet0/0 IP
address to get a full score.

QUESTION 2（DMVPN）を全要件に合わせて解説します。

***

## Topology 解説

| デバイス | インターフェース | IPアドレス | 役割 |
| :-- | :-- | :-- | :-- |
| HUB | E0/0 | 172.16.0.254/24 | DC側LAN |
| HUB | E0/1 | 10.10.255.254/24 | ISP側（NBMA） |
| HUB | Tunnel0 | 192.168.1.254/24 | DMVPNトンネル（NHSサーバ） |
| HUB | Loopback0 | 10.10.1.1/32 | ルータID |
| BR1 | E0/1 | 10.10.255.1/24 | ISP側（NBMA） |
| BR1 | E0/0 | 172.16.1.254/24 | ブランチLAN |
| BR1 | Tunnel0 | 192.168.1.1/24 | DMVPNトンネル（Spoke） |
| BR2 | E0/1 | 10.10.255.2/24 | ISP側（NBMA） |
| BR2 | E0/0 | 172.16.2.254/24 | ブランチLAN |
| BR2 | Tunnel0 | 192.168.1.2/24 | DMVPNトンネル（Spoke） |

**構成の要点：** HUBとBR1/BR2はISPクラウド（10.10.255.0/24）経由でつながる。Tunnel0は仮想的なオーバーレイネットワーク（192.168.1.0/24）上に張られるDMVPN Phase 3構成。Spoke同士（BR1⇔BR2）が直接トンネル通信できることがゴール。

***

## タスク文の翻訳と意味

**全体前提（General Requirement）**
> DMVPNネットワークはHUBのTunnel0 IPアドレス192.168.1.254、IP接続性、cryptoポリシー/プロファイル、EIGRP AS100が事前設定済み。NHRPパスワードはccnp123。NetworkIDとtunnel keyはEIGRP ASN（=100）。スタティックルートは追加禁止。物理インターフェースをtunnel sourceとして使い、BR1・BR2からHUBへのDMVPN接続を設定せよ。


| Task | 日本語訳 | 意味 |
| :-- | :-- | :-- |
| **Task 1** | BR1でNHRP認証・スタティックNBMAマッピング・ホールドタイム5分・ネットワークID・NHSサーバを設定 | BR1がHUBを「NHRPサーバ」として登録し、トンネルを確立できるようにする |
| **Task 2** | BR2に同様のNHRP設定を行う | BR2をDMVPNに参加させる |
| **Task 3** | 暗号化前にフラグメントが行われるよう、Tunnel0のIP MTUを1400、TCP MSS調整を1360に設定 | GRE+IPsecヘッダのオーバーヘッドを考慮しパケットロスを防ぐ |
| **Task 4** | TunnelにIPsecプロファイルを適用し、BR1⇔BR2間のSpoke-to-Spoke通信をtracerouteで確認 | Phase 3 DMVPNでSpokeが直接通信できることを証明する |


***

## 使用するLAB：**General LAB**

| LABデバイス | 役割 |
| :-- | :-- |
| R1 | HUB |
| R2 | BR1 |
| R3 | BR2 |
| S1（スイッチ経由） | ISPクラウド（10.10.255.0/24）の共有セグメント |


***

## Pre-setting（事前設定コマンド）

### HUB（R1）

```
enable
configure terminal
hostname HUB
interface loopback 0
 ip address 10.10.1.1 255.255.255.255
 no shutdown
interface gigabitEthernet 0/0
 ip address 172.16.0.254 255.255.255.0
 no shutdown
interface gigabitEthernet 0/1
 ip address 10.10.255.254 255.255.255.0
 no shutdown
crypto isakmp policy 10
 encr aes
 authentication pre-share
 group 2
crypto isakmp key ccnp123 address 0.0.0.0
crypto ipsec transform-set TSET esp-aes esp-sha-hmac
 mode transport
crypto ipsec profile ccnp
 set transform-set TSET
interface tunnel 0
 ip address 192.168.1.254 255.255.255.0
 tunnel source gigabitEthernet 0/1
 tunnel mode gre multipoint
 tunnel key 100
 ip nhrp authentication ccnp123
 ip nhrp map multicast dynamic
 ip nhrp network-id 100
 ip nhrp redirect
 tunnel protection ipsec profile ccnp
router eigrp 100
 network 10.10.1.0 0.0.0.255
 network 172.16.0.0 0.0.0.255
 network 192.168.1.0
end
copy run start
```


### BR1（R2）

```
enable
configure terminal
hostname BR1
interface loopback 0
 ip address 10.10.10.1 255.255.255.255
 no shutdown
interface gigabitEthernet 0/1
 ip address 10.10.255.1 255.255.255.0
 no shutdown
interface gigabitEthernet 0/2
 ip address 172.16.1.254 255.255.255.0
 no shutdown
crypto isakmp policy 10
 encr aes
 authentication pre-share
 group 2
crypto isakmp key ccnp123 address 0.0.0.0
crypto ipsec transform-set TSET esp-aes esp-sha-hmac
 mode transport
crypto ipsec profile ccnp
 set transform-set TSET
interface tunnel 0
 ip address 192.168.1.1 255.255.255.0
router eigrp 100
 network 10.10.10.0 0.0.0.255
 network 172.16.1.0 0.0.0.255
 network 192.168.1.0
end
copy run start
```


### BR2（R3）

```
enable
configure terminal
hostname BR2
interface loopback 0
 ip address 10.10.10.2 255.255.255.255
 no shutdown
interface gigabitEthernet 0/1
 ip address 10.10.255.2 255.255.255.0
 no shutdown
interface gigabitEthernet 0/3
 ip address 172.16.2.254 255.255.255.0
 no shutdown
crypto isakmp policy 10
 encr aes
 authentication pre-share
 group 2
crypto isakmp key ccnp123 address 0.0.0.0
crypto ipsec transform-set TSET esp-aes esp-sha-hmac
 mode transport
crypto ipsec profile ccnp
 set transform-set TSET
interface tunnel 0
 ip address 192.168.1.2 255.255.255.0
router eigrp 100
 network 10.10.10.0 0.0.0.255
 network 172.16.2.0 0.0.0.255
 network 192.168.1.0
end
copy run start
```


***

## ③ 作業前に確認すべき項目と理由

本番試験では、必ず以下を `show run` で確認してから設定を始める。


| 確認コマンド | 確認内容 | 理由 |
| :-- | :-- | :-- |
| `show run | section tunnel` | Tunnel0のIP・既存設定の有無 | 既存設定を上書き・削除しないため |
| `show run | section eigrp` | EIGRP AS番号の確認 | tunnel keyとnetwork-idに使うASNを特定 |
| `show run | section crypto` | IPsecプロファイル名の確認 | Task 4で使うプロファイル名（=`ccnp`）を確認 |
| `show run | section nhrp` | NHRPが既に入っていないか確認 | 重複設定を防ぐ |
| `show ip interface brief` | 物理IFのIP・UP状態確認 | tunnel sourceに使うIFとHUBのNBMA IPを確認 |


***

## ④⑤ Task別 正解コマンドと解説


***

### ✅ Task 1：BR1のNHRP設定

```
enable
configure terminal
interface tunnel 0
tunnel mode gre multipoint
tunnel source gigabitEthernet 0/1
tunnel key 100
ip nhrp authentication ccnp123
ip nhrp map 192.168.1.254 10.10.255.254
ip nhrp map multicast 10.10.255.254
ip nhrp holdtime 300
ip nhrp network-id 100
ip nhrp nhs 192.168.1.254
end
copy run start
```

**解説：**


| コマンド | 意味 |
| :-- | :-- |
| `tunnel mode gre multipoint` | mGREモードに変更。複数のSpokeが同一のTunnel IFから通信可能になる |
| `tunnel source gigabitEthernet 0/1` | 問題文「物理インターフェースをtunnel sourceに使う」の指示に従いE0/1を指定 |
| `tunnel key 100` | EIGRP ASN=100をtunnel keyとして設定（問題文「tunnel key is EIGRP ASN」） |
| `ip nhrp authentication ccnp123` | NHRPパスワード認証。HUBと一致させる必要がある |
| `ip nhrp map 192.168.1.254 10.10.255.254` | HUBのTunnelIP（192.168.1.254）とNBMA IP（10.10.255.254）のスタティックマッピング |
| `ip nhrp map multicast 10.10.255.254` | EIGRPなどのマルチキャストをHUBのNBMA IPへ転送するよう指定 |
| `ip nhrp holdtime 300` | 5分=300秒のホールドタイム（問題文「hold time 5 minutes」） |
| `ip nhrp network-id 100` | NHRP NetworkID=100（EIGRP ASN=100） |
| `ip nhrp nhs 192.168.1.254` | NHSサーバとしてHUBのTunnel IP（192.168.1.254）を指定 |


***

### ✅ Task 2：BR2のNHRP設定

```
enable
configure terminal
interface tunnel 0
tunnel mode gre multipoint
tunnel source gigabitEthernet 0/1
tunnel key 100
ip nhrp authentication ccnp123
ip nhrp map 192.168.1.254 10.10.255.254
ip nhrp map multicast 10.10.255.254
ip nhrp holdtime 300
ip nhrp network-id 100
ip nhrp nhs 192.168.1.254
end
copy run start
```

**解説：** Task 1と全く同じ内容。BR2も同じHUBに登録するSpokeなので設定は同一。唯一の違いはBR2自身のTunnel0 IPが192.168.1.2になっている点だが、NHRPの設定コマンド自体は変わらない。

***

### ✅ Task 3：BR1とBR2のMTU/MSS設定

**BR1:**

```
enable
configure terminal
interface tunnel 0
ip mtu 1400
ip tcp adjust-mss 1360
end
copy run start
```

**BR2:**

```
enable
configure terminal
interface tunnel 0
ip mtu 1400
ip tcp adjust-mss 1360
end
copy run start
```

**解説：**


| コマンド | 意味 |
| :-- | :-- |
| `ip mtu 1400` | Tunnel0のIP MTUを1400バイトに設定。GRE(24B)+IPsec(約50B)のオーバーヘッドを差し引いた値。**暗号化前にフラグメント**が行われるため「fragmentation is done before encryption」が実現される |
| `ip tcp adjust-mss 1360` | TCPのSYNパケットのMSSを1360に書き換える。MTU 1400からTCPヘッダ(20B)+IPヘッダ(20B)を引いた値。大きなTCPセグメントによるフラグメントを防止 |


***

### ✅ Task 4：IPsecプロファイル適用とSpoke-to-Spoke確認

**BR1:**

```
enable
configure terminal
interface tunnel 0
tunnel protection ipsec profile ccnp
ip nhrp shortcut
end
copy run start
```

**BR2:**

```
enable
configure terminal
interface tunnel 0
tunnel protection ipsec profile ccnp
ip nhrp shortcut
end
copy run start
```

**Spoke-to-Spoke traceroute（設定後に実行）：**

```
BR1# traceroute 172.16.2.254
BR2# traceroute 172.16.1.254
```

**解説：**


| コマンド | 意味 |
| :-- | :-- |
| `tunnel protection ipsec profile ccnp` | 事前設定済みのIPsecプロファイル`ccnp`をTunnelに適用。トンネル通信が暗号化される |
| `ip nhrp shortcut` | Phase 3 DMVPNのキー設定。HUBからの`ip nhrp redirect`メッセージを受け取ったSpoke が、相手SpokeへのNHRP解決を行い**直接トンネル**を張れるようになる |

**tracerouteの意味：**

- `traceroute 172.16.2.254` の出力に `192.168.1.2`（BR2のTunnel IP）が表示されれば、HUBを経由せず**BR1→BR2直接**で通信できている証拠
- HUBを経由している場合は `192.168.1.254` が経路に表示される（不合格）

***

## ⑥ 検証コマンドと確認ポイント

### `show ip nhrp`

```
BR1# show ip nhrp
```

- **何を見るか：** `192.168.1.254/32` のエントリで、NBMA IP（10.10.255.254）が登録されているか
- **正常な状態：** `Flags: authoritative registered used nhop` などが表示される


### `show ip nhrp detail`

```
BR1# show ip nhrp detail
```

- **何を見るか：** BR2（192.168.1.2）が動的に登録されているか（Spoke-to-Spoke成立後）
- **正常な状態：** `Type: dynamic` のエントリがBR2のIPで表示される


### `show ip route eigrp`

```
BR1# show ip route eigrp
```

- **何を見るか：** `172.16.2.0/24`（BR2のLAN）がEIGRP経由で学習されているか
- **正常な状態：** `D 172.16.2.0/24 via 192.168.1.254` または `192.168.1.2` が表示


### `show crypto ipsec sa`

```
BR1# show crypto ipsec sa
```

- **何を見るか：** `#pkts encaps`（暗号化済みパケット数）と `#pkts decaps`（復号済みパケット数）が増えているか
- **正常な状態：** pingやtraceroute後に両カウンタが 0 より大きくなっている


### `show dmvpn`

```
BR1# show dmvpn
```

- **何を見るか：** HUBエントリのStateが `UP` になっているか
- **正常な状態：** `NHRP Peers: 1` で State=`UP`、Intf=`Tu0` が表示される


### `ping 192.168.1.254`（HUBへのトンネル疎通）

```
BR1# ping 192.168.1.254
```

- **何を見るか：** `!!!!!` が返るか
- **意味：** NHRPとIPsecが正常に動作しHUBとのトンネルが確立している


### `traceroute 172.16.2.254`（Spoke-to-Spoke確認）

```
BR1# traceroute 172.16.2.254
```

- **何を見るか：** ホップが `192.168.1.2`（BR2のTunnel IP）を経由しているか
- **合格条件：** HUB（192.168.1.254）が経路に現れず、BR2（192.168.1.2）へ直接到達している

***

## 本番試験での注意点

| チェック | 内容 |
| :-- | :-- |
| `show run` で確認してから設定開始 | IPsecプロファイル名・EIGRP AS番号を必ず目視確認 |
| `tunnel key` を忘れない | 問題文の「tunnel key is EIGRP ASN」を見落としやすい |
| Task 1・2 の両方に設定 | BR1だけ設定しBR2を忘れるミスが多い |
| `copy run start` を各Task後に実行 | 指示に「Save to NVRAM」と明記されている |
| traceroute後に正解確認 | `192.168.1.2` を経由していなければTask 4は不完全 |

<span style="display:none">[^1]</span>

<div align="center">⁂</div>

[^1]: image.jpg

