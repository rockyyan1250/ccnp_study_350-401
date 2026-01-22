# QUESTION 12

# R10
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.2.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.1 255.255.255.0
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 vrf forwarding CORP
 ip address 10.100.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.10.1.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
ip route vrf CORP 10.101.2.0 255.255.255.0 Tunnel0 10.100.100.2
!
end


# R20
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.1.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.2 255.255.255.0
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.101
 encapsulation dot1Q 101
 vrf forwarding CORP
 ip address 10.101.2.1 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.10.2.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
ip route vrf CORP 10.100.1.0 255.255.255.0 Tunnel0 10.100.100.1
!
end


# 回答
# R10
enable
configure terminal
interface Tunnel0
 tunnel source 10.10.1.1
 tunnel destination 10.10.2.1
 tunnel protection ipsec profile MyProfile
end

# R20
enable
configure terminal
interface Tunnel0
 tunnel source 10.10.2.1
 tunnel destination 10.10.1.1
 tunnel protection ipsec profile MyProfile
end


----------------------------------------------------------------------------------------
# QUESTION 21

# R10
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 vrf forwarding CORP
 ip address 10.100.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.10.1.1 255.255.255.0
!
interface Tunnel0
 ip address 10.100.100.1 255.255.255.0
!
end



# R20
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.101
 encapsulation dot1Q 101
 vrf forwarding CORP
 ip address 10.101.2.1 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.10.2.1 255.255.255.0
!
interface Tunnel0
 ip address 10.100.100.2 255.255.255.0
!
end




----------------------------------------------------------------------------------------
# QUESTION 25

# R10
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.2.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.1 255.255.255.0
 tunnel destination 10.10.2.1
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 vrf forwarding CORP
 ip address 10.100.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.10.1.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
end


# R20
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.1.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.2 255.255.255.0
 tunnel destination 10.10.1.1
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.101
 encapsulation dot1Q 101
 vrf forwarding CORP
 ip address 10.101.2.1 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.10.2.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
end

----------------------------------------------------------------------------------------
# QUESTION 26

# R10

enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.2.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 ip address 10.100.100.1 255.255.255.0
 tunnel source GigabitEthernet0/1
 tunnel destination 10.10.2.1
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 ip address 10.100.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.10.1.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
ip route vrf CORP 10.101.2.0 255.255.255.0 Tunnel0 10.100.100.2


# R20
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.1.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface Tunnel0
 ip address 10.100.100.2 255.255.255.0
 tunnel source GigabitEthernet0/2
 tunnel destination 10.10.1.1
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.101
 encapsulation dot1Q 101
 ip address 10.101.2.1 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.10.2.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
ip route vrf CORP 10.100.1.0 255.255.255.0 Tunnel0 10.100.100.1
end



----------------------------------------------------------------------------------------
# QUESTION 27
# R10
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.2.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.100
 encapsulation dot1Q 100
 vrf forwarding CORP
 ip address 10.100.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.10.1.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.1 255.255.255.0
 tunnel source GigabitEthernet0/1
!
end

# R20
enable
configure terminal
vrf definition CORP
 address-family ipv4
 exit-address-family
!
crypto isakmp policy 10
 encr aes
 hash md5
 authentication pre-share
 group 2
crypto isakmp key cisco address 10.10.1.1
!
crypto ipsec transform-set MYSET esp-aes esp-md5-hmac
 mode tunnel
!
crypto ipsec profile MyProfile
 set transform-set MYSET
!
!
interface GigabitEthernet0/0
 no ip address
!
interface GigabitEthernet0/0.101
 encapsulation dot1Q 101
 vrf forwarding CORP
 ip address 10.101.2.1 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.10.2.1 255.255.255.0
 ip ospf network point-to-point
 ip ospf 100 area 0.0.0.0
!
interface Tunnel0
 vrf forwarding CORP
 ip address 10.100.100.2 255.255.255.0
 tunnel source GigabitEthernet0/2
!
end


----------------------------------------------------------------------------------------
# QUESTION 31

初期設定（LAB環境用）

# ISP（R1）
enable
conf t
hostname ISP
interface g0/2
 ip address 209.165.200.229 255.255.255.252
 no shut
interface g0/3
 ip address 209.165.201.1 255.255.255.252
 no shut
end


# R11（R2）
enable
conf t
hostname R11
vrf definition Finance
 address-family ipv4
 exit-address-family
 exit
interface Loopback0
 vrf forwarding Finance
 ip address 10.11.11.1 255.255.255.252
 exit
interface g0/0
 ip address 209.165.200.230 255.255.255.252
 no shut
 exit
ip route 0.0.0.0 0.0.0.0 209.165.200.229
interface Tunnel10
 vrf forwarding Finance
 ip address 10.10.10.1 255.255.255.252
 tunnel source g0/1
 tunnel destination 209.165.201.2
 no shut
 exit
ip route vrf Finance 10.22.22.0 255.255.255.0 Tunnel10 10.10.10.2
end


# R22（R3）初期状態
enable
conf t
hostname R22
vrf definition Finance
 address-family ipv4
 exit-address-family
!
interface Loopback0
 ip address 10.2.2.2 255.255.255.255
!
interface g0/0
 ip address 209.165.201.2 255.255.255.252
!
interface g0/1
 ip address 10.22.22.1 255.255.255.252
!
router bgp 65502
 bgp router-id 10.2.2.2
 network 209.165.201.0 mask 255.255.255.252
 neighbor 209.165.201.1 remote-as 65500
 exit
end



# LAB用（g0表記 / R3=R22役）
conf t
interface Tunnel10
 vrf forwarding Finance
 ip address 10.10.10.2 255.255.255.252
 tunnel source g0/1
 tunnel destination 209.165.200.230
 no shut
 exit
interface Loopback1
 vrf forwarding Finance
 ip address 10.22.22.1 255.255.255.252
 exit
ip route vrf Finance 10.11.11.0 255.255.255.0 Tunnel10 10.10.10.1
end


# 試験用（e0表記 / R22）
R22
en
config t
 int tu10
 vrf forwarding Finance
 ip address 10.10.10.2 255.255.255.252
 tunnel source e0/0
 tunnel destination 209.165.200.230
!
int e0/1
 vrf forwarding Finance
 ip address 10.22.22.1 255.255.255.252
!
ip route vrf Finance 10.10.111.0 255.255.255.0 tu10 10.10.10.1
end
copy run start

# 動作確認 (Verification)
ping vrf Finance 10.10.10.1
--------------------------------------------------------------------------------------------------------

# QUESTION 32

# R10役（R2）

enable
conf t
hostname R10
interface g0/3
 ip address 10.10.20.10 255.255.255.0
 no shut
exit
router ospf 10
 network 10.10.20.0 0.0.0.255 area 0
end


# R40役（R4）

enable
conf t
hostname R40
interface g0/3
 ip address 10.40.50.40 255.255.255.0
 no shut
exit
router ospf 10
 network 10.40.50.0 0.0.0.255 area 40
end

# R20役（R3）問題の初期状態
enable
conf t
hostname R20
interface Loopback0
 ip address 10.0.1.20 255.255.255.255
 exit
interface Loopback1
 ip address 10.20.20.20 255.255.255.255
 exit
interface g0/0
 ip address 10.10.20.20 255.255.255.0
 no shut
 exit
interface g0/1
 ip address 10.10.30.20 255.255.255.0
 no shut
interface g0/2
  ip address 10.40.50.20 255.255.255.0
 exit
end

# LAB環境用：解答（Solution / R3=R20役）

conf t
router ospf 10
 router-id 10.20.20.20
 network 10.0.1.20 0.0.0.0 area 0
 network 10.20.20.20 0.0.0.0 area 0
 network 10.10.20.0 0.0.0.255 area 0
 network 10.40.50.0 0.0.0.255 area 40
 area 40 range 10.40.0.0 255.255.240.0
end

# 正解コマンド（Exam想定 / R20）

R20
en
config t
router ospf 10
router-id 10.20.20.20
network 10.0.1.20 0.0.0.0 area 0
network 10.20.20.20 0.0.0.0 area 0
network 10.10.20.0 0.0.0.255 area 0
network 10.10.30.0 0.0.0.255 area 0
network 10.40.50.0 0.0.0.255 area 40
area 40 range 10.40.0.0 255.255.240.0
end
copy run start

-----------------------------------------------------------------------------------------------------

# QUESTION 33

# R10役 (R2) の設定

enable
conf t
hostname R10
interface g0/3
 ip address 10.10.20.10 255.255.255.0
 no shut
exit
router ospf 200
 network 10.10.20.0 0.0.0.255 area 0
end


# R40役 (R4) の設定

enable
conf t
hostname R40
interface g0/3
 ip address 10.40.50.40 255.255.255.0
 no shut
exit
router ospf 200
 network 10.40.50.0 0.0.0.255 area 40
end

# R20役 (R3) の初期設定

enable
conf t
hostname R20
interface Loopback0
 ip address 10.0.1.20 255.255.255.255
exit
interface Loopback1
 ip address 10.20.20.20 255.255.255.255
exit
interface g0/0
 ip address 10.10.20.20 255.255.255.0
 no shut
exit
interface g0/1
 ip address 10.10.30.20 255.255.255.0
 no shut
interface g0/2
 ip address 10.40.50.20 255.255.255.0
 no shut

exit
end

# 動作確認
R3 (R20役) で実行
show ip ospf neighbor
FULL または 2WAY

-----------------------------------------------------------------------------------------------

# QUESTION 34 


# Sw1 (R10), Sw2 (R20), Sw3 (R30) すべてで実行
enable
conf t
ip routing
interface range g0/0 - 3, g1/0 - 3
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shut
exit
vlan 123
 exit
interface vlan 123
 no shut
end

# R10 (Sw1) の初期設定
en
conf t
hostname R10
interface vlan 123
 ip address 192.168.123.10 255.255.255.0
 exit
router ospf 10
 router-id 192.168.1.10
 network 192.168.1.10 0.0.0.0 area 0
 network 192.168.123.0 0.0.0.255 area 0
 exit
ip access-list extended 120
 10 permit tcp any any
 20 permit udp any any
 30 permit icmp any any
 40 deny ip any any
 exit
interface vlan 123
 ip access-group 120 in
end


# R20 (Sw2) の初期設定

en
conf t
hostname R20
interface vlan 123
 ip address 192.168.123.20 255.255.255.0
 exit
router ospf 10
 router-id 192.168.1.20
 network 192.168.123.0 0.0.0.255 area 0
end

# R30 (Sw3) の初期設定

en
conf t
hostname R30
interface vlan 123
 ip address 192.168.123.30 255.255.255.0
 exit
router ospf 10
 router-id 192.168.1.30
 network 192.168.123.0 0.0.0.255 area 0
end

# 解答コマンド
# R10 (Sw1)
configure terminal
ip access-list extended 120
 5 permit ospf any any
end

# R30 (Sw3)
configure terminal
access-list 100 permit tcp 192.168.24.0 0.0.0.255 any eq 23
class-map telnet24
 match access-group 100
 exit
policy-map copp
 class telnet24
  police cir 8000 conform-action transmit exceed-action drop
 exit
exit
control-plane
 service-policy input copp
end

# 動作確認
R30#sh access-list 100
Extended IP access list 100
10 permit tcp 192.168.24.0 0.0.0.255 any eq telnet


R30#sh policy-map control-plane
Control Plane
Service-policy input: copp
Class-map: telnet24 (match-all)
0 packets, 0 bytes
5 minute offered rate 0000 bps, drop rate 0000 bps
Match: access-group 100
police:
cir 8000 bps, bc 1500 bytes
conformed 0 packets, 0 bytes; actions:
transmit
exceeded 0 packets, 0 bytes; actions:
drop
conformed 0000 bps, exceeded 0000 bps
Class-map: class-default (match-any)
22 packets, 2832 bytes
5 minute offered

---------------------------------------------------------------------------------------------------------
# QUESTION 35

# Sw1（R1役 / AS10）初期状態

enable
configure terminal
hostname R1
ip routing
!
interface loopback0
 ip address 10.1.1.10 255.255.255.255
!
interface loopback10
 ip address 209.165.201.10 255.255.255.255
!
interface loopback20
 ip address 209.165.201.20 255.255.255.255
!
interface g0/0
 no switchport
 ip address 209.165.200.224 255.255.255.252
 no shutdown
!
interface g0/1
 no switchport
 ip address 209.165.202.128 255.255.255.252
 no shutdown
end

# Sw2（R2役 / AS20）初期状態
enable
configure terminal
hostname R2
ip routing
!
interface g1/0
 no switchport
 ip address 209.165.200.226 255.255.255.252
 no shutdown
!
router bgp 20
 bgp router-id 2.2.2.2
 neighbor 209.165.200.225 remote-as 10
 address-family ipv4
  neighbor 209.165.200.225 activate
 exit-address-family
end

# Sw3（R3役 / AS30）初期状態
enable
configure terminal
hostname R3
ip routing
!
interface g1/1
 no switchport
 ip address 209.165.202.130 255.255.255.252
 no shutdown
!
router bgp 30
 bgp router-id 3.3.3.3
 neighbor 209.165.202.129 remote-as 10
 address-family ipv4
  neighbor 209.165.202.129 activate
 exit-address-family
end

# Sw1（R1役）解答コマンド
enable
configure terminal
router bgp 10
 bgp router-id 10.1.1.10
 neighbor 209.165.200.226 remote-as 20
 neighbor 209.165.202.130 remote-as 30
 address-family ipv4
  neighbor 209.165.200.226 activate
  neighbor 209.165.202.130 activate
  network 209.165.200.224 mask 255.255.255.252
  network 209.165.202.128 mask 255.255.255.252
  network 10.1.1.10 mask 255.255.255.255
  network 209.165.201.10 mask 255.255.255.255
  network 209.165.201.20 mask 255.255.255.255
 exit-address-family
end
write memory

# 確認コマンド
R1# sh run | s router bgp

-----------------------------------------------------------------------------------------------------------------------
# QUESTION 36

# 初期状態（Pre-config）
# R4（Sw20相当 / L2）
enable
conf t
hostname Sw20
vlan 123
vlan 24
interface range g0/0-3
 switchport mode trunk
 switchport trunk allowed vlan 123,24
 no shut
end

# R1（R10相当 / L3）
enable
conf t
hostname R10
interface loopback0
 ip address 192.168.1.10 255.255.255.255
interface g0/0
 ip address 192.168.123.10 255.255.255.0
router eigrp 10
 network 192.168.1.10 0.0.0.0
 network 192.168.123.0 0.0.0.255
end

# R2（R20相当 / L3）
enable
conf t
hostname R20
ip routing
interface loopback0
 ip address 192.168.1.20 255.255.255.255
!
interface g0/0
 ip address 192.168.123.20 255.255.255.0
!
interface g0/1
 ip address 192.168.24.20 255.255.255.0
!
router eigrp 10
 network 192.168.1.20 0.0.0.0
 network 192.168.24.0 0.0.0.255
 network 192.168.123.0 0.0.0.255
end

# R3（R30相当 / L3）※ACL120が既に適用されている状態を再現

enable
conf t
hostname R30
ip routing
interface loopback0
 ip address 192.168.1.30 255.255.255.255
!
interface g0/0
 ip address 192.168.123.30 255.255.255.0
 ip access-group 120 in
!
router eigrp 10
 network 192.168.1.30 0.0.0.0
 network 192.168.123.0 0.0.0.255
access-list 120 permit tcp any any
access-list 120 permit udp any any
access-list 120 permit icmp any any
access-list 120 deny ip any any
end

# 解答
# Task 1（R30=Sw3）
enable
conf t
ip access-list extended 120
 5 permit eigrp any any
end
copy run start

# Task 2（R20=Sw2）
enable
conf t
access-list 100 permit tcp host 192.168.24.124 any eq 23
class-map match-all pc20-telnet
 match access-group 100
policy-map copp-policy
 class pc20-telnet
  police 10000 conform-action transmit exceed-action drop
control-plane
 service-policy input copp-policy
end
copy run start

------------------------------------------------------------------------------------------------------------------
# QUESTION 37

（Sw1–Sw4）

Sw1 = Sw10（変更可能なのはここだけ）

Sw4 = Sw20（触れない想定だが、再現のため初期設定は入れる）

Sw3 = Sw30（触れない想定だが、再現のため初期設定は入れる）

Sw2は未使用（電源OFFでもOK）

# Sw1（Sw10役

enable
conf t
hostname Sw10
vlan 10
vlan 30
!
interface Port-channel1
 switchport access vlan 10
 switchport mode access
!
interface range g0/0-2
 switchport access vlan 10
 switchport mode access
!
interface g0/3
 switchport access vlan 30
 switchport mode access
!
interface g1/0
 switchport access vlan 30
 switchport mode access
!
interface vlan 10
 ip address 10.100.10.10 255.255.255.0
 no shut
!
interface vlan 30
 ip address 10.100.20.10 255.255.255.0
 no shut
end

# Sw4（Sw20役

enable
conf t
hostname Sw20
vlan 10
vlan 30
!
interface range g0/0-2
 switchport mode trunk
 channel-group 1 mode active
 no shut
!
interface Port-channel1
 switchport mode trunk
 no shut
end

# Sw3（Sw30役

enable
conf t
hostname Sw30
vlan 10
vlan 30
!
interface range g0/0-2
 switchport mode trunk
 channel-group 1 mode active
 no shut
!
interface Port-channel1
 switchport mode trunk
 no shut
end

# Solution（解答：Sw10＝Sw1だけ変更

enable
conf t
spanning-tree vlan 10,30 root primary
end

enable
conf t
interface range g0/0-2
 switchport mode dynamic desirable
 channel-group 1 mode active
!
interface Port-channel1
 switchport mode dynamic desirable
 shutdown
 no shutdown
end
copy run start

# 確認コマンド（Sw10＝Sw1で実行）
show etherchannel 1 summary
show interfaces trunk
show spanning-tree vlan 10
show spanning-tree vlan 30



----------------------------------------------------------------------------------------
# QUESTION 38
環境マッピング（General）

# R1（問題開始前）

enable
configure terminal
hostname R1
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 10.10.1.2 255.255.255.0
 ip flow monitor Monitor-NetFlowENCOR input
 ip flow monitor Monitor-NetFlowENCOR output
 ip ospf network point-to-point
 no shutdown
!
flow exporter Export-NetFlowENCOR
 source Loopback0
 transport udp 2055
!
flow monitor Monitor-NetFlowENCOR
 exporter Export-NetFlowENCOR
 cache timeout inactive 60
 cache timeout active 600
 record netflow ipv4 original-input
!
router ospf 10
 router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0 area 0
 network 10.10.1.0 0.0.0.255 area 0
end


# S1

enable
configure terminal
!
interface Loopback0
 ip address 10.2.2.2 255.255.255.255
!
interface GigabitEthernet0/0
 switchport access vlan 10
 ip flow ingress
 ip flow egress
!
interface GigabitEthernet0/1
 switchport access vlan 12
 ip flow ingress
 ip flow egress
!
interface GigabitEthernet0/2
 switchport access vlan 14
 ip flow ingress
 ip flow egress
!
interface Vlan10
 ip address 10.10.1.1 255.255.255.0
 ip ospf network point-to-point
!
interface Vlan12
 ip address 10.12.1.1 255.255.255.0
!
interface Vlan14
 ip address 10.14.1.1 255.255.255.0
!
router ospf 10
 router-id 10.2.2.2
 network 10.2.2.2 0.0.0.0 area 0
 network 10.10.1.0 0.0.0.255 area 0
 network 10.12.1.0 0.0.0.255 area 0
 network 10.14.1.0 0.0.0.255 area 0
end

# 回答
# R1
enable
configure terminal
flow exporter Export-NetFlowENCOR
 destination 10.10.1.110
exit
ip sla 1
 http get http://10.10.1.100
 frequency 300
exit
ip sla schedule 1 life forever start-time now
end

# S1
enable
configure terminal
monitor session 7 source interface g0/0 both
monitor session 7 destination interface g1/1
en


----------------------------------------------------------------------------------------
# QUESTION 39
#  R1（AS 65100）
enable
configure terminal
hostname R1
!
interface GigabitEthernet0/1
 no ip address
!
interface Loopback0
 ip address 192.168.1.1 255.255.255.255
!
interface g0/0
 ip address 209.165.200.225 255.255.255.252
 no shutdown
!
interface g0/1
 ip address 209.165.202.129 255.255.255.252
 no shutdown
!
router bgp 65100
 bgp router-id 192.168.1.1
 neighbor 209.165.200.226 remote-as 65200
 neighbor 209.165.202.130 remote-as 65300
end

#  R2（AS 65200）
enable
configure terminal
hostname R2
!
interface GigabitEthernet0/2
 no ip address
!
interface Loopback0
 ip address 192.168.2.2 255.255.255.255
!
interface Loopback1
 ip address 209.165.201.1 255.255.255.255
!
interface Loopback2
 ip address 209.165.201.2 255.255.255.255
!
interface g0/0
 ip address 209.165.200.226 255.255.255.252
 no shutdown
!
interface g0/1
 ip address 209.165.200.230 255.255.255.252
 no shutdown
end


#  R3（AS 65300）
enable
configure terminal
hostname R3
!
interface  GigabitEthernet0/3
 no ip address
!
interface Loopback0
 ip address 192.168.3.3 255.255.255.255
!
interface g0/0
 ip address 209.165.202.130 255.255.255.252
 no shutdown
!
interface g0/1
 ip address 209.165.200.229 255.255.255.252
 no shutdown
!
router bgp 65300
 bgp router-id 192.168.3.3
 neighbor 209.165.200.230 remote-as 65200
 neighbor 209.165.202.129 remote-as 65100
end

#  回答
#  R2 
configure terminal
router bgp 65200
 bgp router-id 192.168.2.2
 neighbor 209.165.200.225 remote-as 65100
 neighbor 209.165.200.229 remote-as 65300
 address-family ipv4
  network 192.168.2.2 mask 255.255.255.255
  network 209.165.201.1 mask 255.255.255.255
  network 209.165.201.2 mask 255.255.255.255
 exit-address-family
end

16 0
17 128
18 192
----------------------------------------------------------------------------------------
# QUESTION 40

# R20
enable
configure terminal
interface Loopback0
 ip address 10.0.1.20 255.255.255.255
!
interface Loopback1
 ip address 10.20.20.20 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 10.10.20.20 255.255.255.0
!
interface GigabitEthernet0/1
 ip address 10.20.30.20 255.255.255.0
!
interface GigabitEthernet0/2
 ip address 10.40.50.20 255.255.255.0
end

# 解答
# R20
enable
configure terminal
router ospf 20
 router-id 10.0.1.20
 area 40 range 10.40.0.0 255.255.192.0
!
interface Loopback0
 ip ospf 20 area 0
!
interface Loopback1
 ip ospf 20 area 0
!
interface GigabitEthernet0/0
 ip ospf 20 area 0
!
interface GigabitEthernet0/1
 ip ospf 20 area 0
!
interface GigabitEthernet0/2
 ip ospf 20 area 40
end

----------------------------------------------------------------------------------------
# QUESTION 41
# R1

enable
configure terminal
flow exporter Export-NetFlowENCOR
 destination 10.10.1.10
 source Loopback0
!
flow monitor Monitor-NetFlowENCOR
 exporter Export-NetFlowENCOR
 cache timeout inactive 60
 cache timeout active 600
 record netflow ipv4 original-input
!
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 10.10.1.2 255.255.255.0
 ip ospf network point-to-point
!
router ospf 10
 router-id 1.1.1.1
 network 1.1.1.1 0.0.0.0 area 0
 network 10.10.1.0 0.0.0.255 area 0
!
ip sla 100
 icmp-echo 10.12.1.2
frequency 300

# Sw1


# 解答
# R1
configure terminal
flow exporter Export-NetFlowENCOR
 transport udp 2055
ip sla schedule 100 life forever start-time now
exit
end

# Sw1
configure terminal
monitor session 11 source interface GigabitEthernet0/1 both
monitor session 11 destination interface GigabitEthernet1/1
end


----------------------------------------------------------------------------------------
# QUESTION 42
# R1
enable
configure terminal
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
!
interface GigabitEthernet0/0
 ip address 10.10.1.2 255.255.255.0
 ip ospf network point-to-point
!
flow exporter Export-FlowR1
 destination 10.10.1.10
 source Loopback0
 transport udp 2055
!
flow monitor Monitor-FlowR1
 exporter Export-FlowR1
 cache timeout inactive 30
 cache timeout active 300
 record netflow ipv4 original-input
!
end


# Sw1
enable
configure terminal
interface Loopback0
 ip address 5.5.5.5 255.255.255.255
!
interface GigabitEthernet0/0
 switchport access vlan 10
 ip flow ingress
 ip flow egress
!
interface GigabitEthernet0/1
 switchport access vlan 12
 ip flow ingress
 ip flow egress
!
interface GigabitEthernet0/2
 switchport access vlan 14
 ip flow ingress
 ip flow egress
!
end

#　回答

#　R1# 
en
configure terminal
interface GigabitEthernet0/0
 ip flow monitor Monitor-FlowR1 input
 ip flow monitor Monitor-FlowR1 output
ip sla 1
 icmp-echo 5.5.5.5
 frequency 60
exit
ip sla schedule 1 life forever start-time now
end

#　Sw1# 
en
configure terminal
monitor session 5 source interface GigabitEthernet0/2 both
monitor session 5 destination interface GigabitEthernet1/0
end
