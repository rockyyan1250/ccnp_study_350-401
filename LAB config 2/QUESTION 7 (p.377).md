
# QUESTION 7もお願いします。

Tasks:
Configure IPSec security policy on tunnel interfaces to ensure data confidentiality and integrity where mGRE tunnels are up and running between HUB and SPOKE
routers.

1. Configure the ISAKMP policy parameters with the following attributes:

- AES256
- SHA256
- Group2
- lifetime 86400

2. Ensure that GRE IP Header should be encrypted inside the IPSec packet. Verify IPSec security association and ISAKMP encrypted key. Use ISAKMP key "abc123".

3. Configure a flexible ISAKMP Policy on the HUB to add peers that have the dynamic IP addresses where SPOKES must add HUB IP static entry using an encrypted
key. Use a single command to configure it. Use IPSec phase-2 transform-set name as 'T-SET' and IPSec Profile name as 'IPSEC-PROFILE'.


QUESTION 7 も同じフォーマットで整理します。

***

## Topology と GRE/IPsec のイメージ

- R0：Hub ルータ。Tunnel0 = 10.0.0.254/24
- R1：Spoke1。Tunnel0 = 10.0.0.1/24
- R2：Spoke2。Tunnel0 = 10.0.0.2/24
- PC1/PC2/PC3 はそれぞれ Hub/Spoke の LAN にぶら下がるクライアント。
- 既に mGRE トンネル（R0 と R1/R2 間）は up、NHRP/OSPF も設定済みで、今から IPsec だけ載せる状況。[^1]

最初の図は「GRE over IPsec」のパケット構造で、**Tunnelモード**では「外側IP + ESP + 内側GRE IPヘッダ＋GRE＋元IP/TCP/Data」を全部暗号化する、一方 **Transportモード**は元IPヘッダをそのまま残してGRE部分だけを暗号化するイメージを示している。[^1]
今回のタスクは「GRE IP Header should be encrypted」なので、**Tunnelモード**を使う必要がある。

***

## タスク文の翻訳と意味

1. 「ISAKMP ポリシーを AES256, SHA256, group2, lifetime 86400 で設定せよ」
→ R0/R1/R2 全部に同じ `crypto isakmp policy` を作る。[^1]

2. 「GRE IP Header が IPsec パケットの内側で暗号化されるようにせよ。IPsec SA と IKE の暗号化キーを検証せよ。ISAKMP key は `abc123` を用いる。」
→ Transform-set を Tunnel モードで作り、HUB は動的IPの Spoke を受け入れられるよう `address 0.0.0.0`、Spoke は HUB の物理IP（192.168.1.2）に対してキーを設定する。[^1]

3. 「HUB では flexible な ISAKMP Policy を1行のコマンドで設定し、動的IPを持つ Spoke を追加可能にする。一方 Spoke 側は HUB のIPを静的に指定して同じ暗号キーを使う。IPsec Phase2 の transform-set 名は `T-SET`、IPsec Profile 名は `IPSEC-PROFILE` とする。」
→ R0 の `crypto isakmp key abc123 address 0.0.0.0` が「単一コマンドで flexible な受け入れ」を意味する。[^1]

***

## 作業前に確認すべき設定と理由

R0/R1/R2 それぞれで以下を確認する。

1. `show run | section Tunnel0`
    - Tunnel IP、tunnel source/destination、NHRP 設定などが既に正しく入っていることを確認。
    - 今回は**トンネルの設定を変えない**のが前提なので、誤って削除しないようにする。[^1]
2. `show run | section crypto`
    - 既存の ISAKMP / IPsec 設定が無いか確認。
    - もし既に `crypto ipsec transform-set` や `crypto ipsec profile` があれば名前が問題文と矛盾しないかチェック。[^1]
3. `show ip route` / `show ip ospf neighbor`
    - 現状でも OSPF 近隣が確立し、トンネル経由でルーティングは通っていることを確認。
    - IPsec を載せた後も OSPF が切れていないか確認するための baseline になる。

***

## 使用LAB

DMVPN / mGRE なので、**CSR LAB** か **General LAB** で 3 ルータ構成を作るのが近いです。

- CSR1 を R0（Hub）、Router2 を R1、もう一台を R2 に見立てて練習すると良い。[^2]

***

## Pre-setting（事前設定コマンド）

問題文に書かれている既存設定を、例として R0/R1/R2 に入れておきます（本番では既に設定済み）。

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

### ✅ Task 1：ISAKMP ポリシーの設定（R0/R1/R2 共通）

**R0**

```
enable
configure terminal
crypto isakmp policy 10
hash sha256
encryption aes 256
group 2
lifetime 86400
authentication pre-share
end
copy run start
```

**R1**

```
enable
configure terminal
crypto isakmp policy 10
hash sha256
encryption aes 256
group 2
lifetime 86400
authentication pre-share
end
copy run start
```

**R2**

```
enable
configure terminal
crypto isakmp policy 10
hash sha256
encryption aes 256
group 2
lifetime 86400
authentication pre-share
end
copy run start
```

**解説：**

- `crypto isakmp policy 10` で IKE Phase1 のポリシーを定義。
- `hash sha256` / `encryption aes 256` / `group 2` / `lifetime 86400` がタスク指定のパラメータ。
- `authentication pre-share` は pre-share key（abc123）を使うので必須。[^1]

***

### ✅ Task 2：GRE IP Header を暗号化し、キーを設定（R0/R1/R2）

**R0（Hub, flexible key受け入れ）**

```
enable
configure terminal
crypto isakmp key abc123 address 0.0.0.0
crypto ipsec transform-set T-SET esp-des esp-md5-hmac
mode tunnel
crypto ipsec profile IPSEC-PROFILE
set transform-set T-SET
interface tunnel 0
tunnel protection ipsec profile IPSEC-PROFILE
end
copy run start
```

**R1（Spoke1, HubのIPを指定）**

```
enable
configure terminal
crypto isakmp key abc123 address 192.168.1.2
crypto ipsec transform-set T-SET esp-des esp-md5-hmac
mode tunnel
crypto ipsec profile IPSEC-PROFILE
set transform-set T-SET
interface tunnel 0
tunnel protection ipsec profile IPSEC-PROFILE
end
copy run start
```

**R2（Spoke2, HubのIPを指定）**

```
enable
configure terminal
crypto isakmp key abc123 address 192.168.1.2
crypto ipsec transform-set T-SET esp-des esp-md5-hmac
mode tunnel
crypto ipsec profile IPSEC-PROFILE
set transform-set T-SET
interface tunnel 0
tunnel protection ipsec profile IPSEC-PROFILE
end
copy run start
```

**解説：**

- `crypto isakmp key abc123 address 0.0.0.0`
    - R0 は「どのピアからでも（動的IP）」abc123 で受け入れる flexible 設定。**1コマンドで dynamic peers を受け入れる**というタスク3の条件を満たす。[^1]
- `crypto isakmp key abc123 address 192.168.1.2`
    - R1/R2 は HUB の物理IP（192.168.1.2）宛にキーを設定し、静的に指定する。
- `crypto ipsec transform-set T-SET esp-des esp-md5-hmac`
    - フェーズ2の transform-set 名を `T-SET` と指定（暗号アルゴリズム自体には条件なし）。
- `mode tunnel`
    - GRE IP Header を含む内側の IP/ GRE / TCP をすべてカプセル化して暗号化するため、**トンネルモード**にする。これが「GRE IP Header should be encrypted」の条件を満たすポイント。[^1]
- `crypto ipsec profile IPSEC-PROFILE` + `set transform-set T-SET`
    - IPsec プロファイルを作成し、Transform-set を紐づける。
- `interface tunnel 0` `tunnel protection ipsec profile IPSEC-PROFILE`
    - DMVPN トンネルインターフェースに IPsec を適用するコマンド。これで Tunnel0 上の全トラフィックが IPsec で保護される。

***

## 検証コマンドと確認ポイント

### 1. IKE / IPsec セッション確認

**IKE SA**

```
show crypto isakmp sa
```

- 状態列に `QM_IDLE` や `MM_ACTIVE` が表示されていれば IKE Phase1/2 が正常。
- R0 で R1/R2 のピアアドレスが見えているか確認。

**IPsec SA**

```
show crypto ipsec sa
```

- `local addr` / `remote addr` がトンネルの送信元/宛先IPになっているか。
- `#pkts encaps` / `#pkts decaps` のカウンタが、トラフィック生成（ping, OSPF）後に増えているか確認。


### 2. OSPF 近隣関係とルーティング

```
show ip ospf neighbor
show ip route
```

- IPsec 適用後も R0–R1, R0–R2 の OSPF ネイバーが `FULL` で維持されているか。
- `10.100.x.0/24` や 10.0.0.0/24 のルートが存在するか。


### 3. エンドツーエンド疎通（PC間のping）

PC1/PC2/PC3 に相当するホストから、それぞれの IP へ ping:

- `ping 10.100.1.10`（PC1→PC2）
- `ping 10.100.2.10`（PC1→PC3）

成功すれば、トンネル上のトラフィックが暗号化されつつエンドツーエンドで通っている。

### 4. GREヘッダが暗号化されているかのイメージ確認

実機試験ではパケットキャプチャはできないが、**Transport モードではなく Tunnel モード**を設定していることが重要。

- `show crypto ipsec sa` 出力の `mode tunnel` を確認して、Tunnelモードになっていることを目視すれば、「GRE IP Header も暗号化される構成」になっていると判断できる。

***

ここまでで QUESTION 7 の DMVPN + IPsec の要件はすべて満たせます。
今の説明の中で、特に自信がない部分（例えば Transform-set の mode の意味、ISAKMP policy のマッチング順序など）はどこかありますか？
<span style="display:none">[^10][^11][^12][^13][^14][^15][^16][^3][^4][^5][^6][^7][^8][^9]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image-2.jpg

[^3]: image.jpg

[^4]: image-2.jpg

[^5]: image.jpg

[^6]: image.jpg

[^7]: image.jpg

[^8]: image.jpg

[^9]: image.jpg

[^10]: image.jpg

[^11]: image.jpg

[^12]: image.jpg

[^13]: image.jpg

[^14]: image.jpg

[^15]: image.jpg

[^16]: image.jpg

