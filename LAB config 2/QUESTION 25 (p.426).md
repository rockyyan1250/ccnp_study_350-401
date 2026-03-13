# QUESTION 25

Task 1:
Use the predefined Sales and Admin VRFs (interfaces configured) to complete the configurations on R2 and R3 using these requirements:
• Use EIGRP process 10
• Do not use MPLS
• The Sales VRF resides in AS 500
• The Admin VRF resides in AS 600
• R3 and R4 must use EIGRP to route traffic
Task 2:
There is packet loss in the Sales VRF when R1 pings R4's Loopback 0. Resolve the issue and confirm these facts:
• R1 and R2 establish EIGRP neighbor relationships in accordance with AS500
• R1 and R4 should advertise and ping each other's Loopback0 in the Sales VRF
Note: Disable automatic summarization in EIGRP on all routers. Do not configure VRFs on R1, R4, R5, and R6.

QUESTION 25 のポイントを、タスク別にコンパクトに整理します。

***

## トポロジと前提

- 上段：EIGRP AS 500（Sales VRF）
    - R1–R2–R3–R4 が 10.0.0.x/30 で直線接続。
- 下段：EIGRP AS 600（Admin VRF）
    - R2–R5、R2–R3–R6 が 10.0.0.24/30, 10.0.0.28/30 など。
- R2/R3 にだけ VRF Admin / Sales が事前定義済みで、インターフェースに vrf forwarding 済み。[^1]

既存の問題点（抜粋）[^1]

- R1 は誤って AS600 で EIGRP 起動。
- R2/R3 の `router eigrp 10` はアドレスファミリ未設定（VRF 内で EIGRP が動いていない）。
- R3 e0/0 に ACL BLOCK1 が in/out 適用され、EIGRP を deny。
- R4/R5/R6 の EIGRP は auto-summary 有効。

***

## Task 1：VRF ごとの EIGRP を構成（AS500/600）

### R2 の設定

```plaintext
enable
configure terminal
router eigrp 10
 address-family ipv4 vrf Sales autonomous-system 500
  network 10.0.0.0 0.0.0.3
  network 10.0.0.4 0.0.0.3
 exit-address-family
 address-family ipv4 vrf Admin autonomous-system 600
  network 10.0.0.24 0.0.0.3
  network 192.168.20.0 0.0.0.3
 exit-address-family
end
copy run start
```

- Sales VRF（AS500）：R1 側 e0/0 の 10.0.0.0/30 と R3 側 e0/1 の 10.0.0.4/30 を広告。
- Admin VRF（AS600）：R5 側 10.0.0.24/30 と R3 側 192.168.20.0/30 を広告。[^1]


### R3 の設定

```plaintext
enable
configure terminal
router eigrp 10
 no auto-summary
 address-family ipv4 vrf Sales autonomous-system 500
  network 10.0.0.8 0.0.0.3
  network 10.0.0.4 0.0.0.3
 exit-address-family
 address-family ipv4 vrf Admin autonomous-system 600
  network 10.0.0.28 0.0.0.3
  network 192.168.20.0 0.0.0.3
 exit-address-family
interface ethernet0/0
 no ip access-group BLOCK1 in
 no ip access-group BLOCK1 out
end
copy run start
```

- Sales VRF：R4 側 10.0.0.8/30 と R2 側 10.0.0.4/30。
- Admin VRF：R6 側 10.0.0.28/30 と R2 側 192.168.20.0/30。
- auto-summary 無効化。
- ACL BLOCK1（`deny eigrp any any`）をイン・アウト両方向で外し、EIGRP パケットを通す。[^1]


### R4/R5/R6 の auto-summary を無効化

```plaintext
! R4
enable
configure terminal
router eigrp 500
 no auto-summary
end

! R5
enable
configure terminal
router eigrp 600
 no auto-summary
end

! R6
enable
configure terminal
router eigrp 600
 no auto-summary
end
```


***

## Task 2：Sales VRF のパケットロス解消（R1–R4 間の EIGRP/到達性）

### R1 の AS 番号修正

```plaintext
enable
configure terminal
no router eigrp 600
router eigrp 500
 network 10.0.0.0 0.0.0.3
 network 10.10.10.1 0.0.0.0
end
copy run start
```

- 正しい AS500 で R2(Sales VRF) と隣接を張る。
- Lo0 10.10.10.1/32 も広告。[^1]

これで:

- R1 ⇔ R2 (VRF Sales, AS500) が EIGRP ネイバー確立。
- R2 ⇔ R3 ⇔ R4 も Sales VRF/AS500 でネイバー確立。
- R1・R4 は互いの Lo0 (10.10.10.1 / 10.10.10.4) を Sales VRF ルーティングテーブルで学習し、ping が両方向成功する。

***

## 仕上げ確認ポイント

- `show ip eigrp vrf Sales neighbors` on R2/R3：R1 と R4 を含む全ネイバーが見える。
- `show ip route vrf Sales 10.10.10.4` on R1：R2→R3→R4 へ続く EIGRP ルートがある。
- `ping vrf Sales 10.10.10.4` from R1 と、R4 から 10.10.10.1 への ping が成功。[^1]

この問題で、VRF 付き EIGRP（address-family）と通常の EIGRP の書き分けはイメージできましたか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

