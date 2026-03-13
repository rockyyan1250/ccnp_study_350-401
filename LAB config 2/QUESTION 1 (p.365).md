# QUESTION 1
Tasks:
Troubleshoot R-WEST to achieve the desired results:

1. All the commands should be locally saved to the router as well as sent to the Syslog server except passwords.
2. All the Cisco OSPF LSA traps should be sent to the SNMP server.

## 使用するLAB：**General LAB**

このトポロジ（R-WEST + Syslog/SNMPサーバ）は General LAB が最適です。[^1]

- **R1 → R-WEST** として使用
- **L1（192.168.0.101）→ Syslog/SNMPサーバ** と見立てる

***

## Pre-setting（事前設定コマンド）

まず General LAB を起動し、R1 に以下を投入してください。これで本番と同じ「前提条件（existing settings）」を再現できます。

```
! ===== R1（R-WESTとして使用）の Pre-setting =====
enable
configure terminal
hostname R-WEST

! Syslogサーバへのlogging設定（IPはL1のIPに合わせる）
logging host 192.168.0.101 sequence-num-session

! SNMP基本設定
snmp-server community public RO
snmp-server host 192.168.0.101 public

! OSPFも動いている前提（trapsを送るため）
router ospf 1
 network 0.0.0.0 255.255.255.255 area 0
 exit

end
copy run start
```


***

## 問題の核心（タスク理解）

| タスク | 意味 |
| :-- | :-- |
| **Task 1** | `archive log config` 機能を使い、コンフィグ変更を①ローカル保存 ②Syslogサーバへ送信（ただしパスワードは除外） |
| **Task 2** | OSPF の **LSA 関連トラップ**のみを SNMP サーバへ送信する |


***

## 正解コマンド（試験本番に入力するもの）

```
R-WEST# enable
R-WEST# configure terminal

! === Task 1: Archive Log Config ===
R-WEST(config)# archive
R-WEST(config-archive)# log config
R-WEST(config-archive-log-cfg)# logging enable      ! ローカルにコンフィグ変更を記録
R-WEST(config-archive-log-cfg)# hidekeys            ! パスワードを隠す（except passwords）
R-WEST(config-archive-log-cfg)# notify syslog       ! Syslogサーバへも送信
R-WEST(config-archive-log-cfg)# exit
R-WEST(config-archive)# exit

! === Task 2: SNMP OSPF LSA Traps ===
R-WEST(config)# snmp-server enable traps ospf lsa

R-WEST(config)# end
R-WEST# copy run start          ! ← 必ず保存！(Save to NVRAM)
```


***

## 必要な知識の解説

### ① Archive Log Config の仕組み

```
archive
 log config
  logging enable     ← コンフィグ変更履歴をローカルに記録
  hidekeys           ← パスワード系コマンドをマスク（"<removed>"と表示）
  notify syslog      ← 変更をリアルタイムでSyslogサーバへ送信
```

- `logging enable` がないと何も記録されない
- `hidekeys` がないと `enable secret cisco123` などがそのまま記録されてしまう（**Task 1 の "except passwords" の要件を満たすためにこれが必須**）
- `notify syslog` は別途 `logging host <IP>` が設定済みであること前提


### ② SNMP Traps の種類（OSPF）

```
snmp-server enable traps ospf ?
  cisco-specific   Cisco独自トラップ
  errors           エラートラップ
  lsa              ★ LSA関連トラップ  ← 今回の答え
  retransmit       再送トラップ
  state-change     ネイバー状態変化
```

**"All the Cisco OSPF LSA traps"** → `ospf lsa` を指定する。`ospf` だけ（サブキーワードなし）では全トラップが対象になるため不正解。

### ③ Pre-configの確認方法（本番試験での作業）

```
R-WEST# show run | section logging
R-WEST# show run | section snmp
R-WEST# show run | section archive
```

このコマンドで **既存のSyslog/SNMPのIPアドレスを確認** してから作業する。既存設定を変更・削除してはいけない。

***

## 検証コマンド

```
! Archive Log Configの確認
R-WEST# show archive log config all
R-WEST# show run | section archive

! SNMP Trapsの確認
R-WEST# show run | include snmp-server enable traps
R-WEST# show snmp

! Syslogの確認
R-WEST# show logging

! 保存確認
R-WEST# show startup-config | section archive
R-WEST# show startup-config | include snmp-server enable traps ospf
```


***

## 本番試験で合格するためのポイント

| チェック項目 | 注意点 |
| :-- | :-- |
| `copy run start` を忘れない | 試験の指示に「Save to NVRAM」と明記 |
| 既存設定を **削除しない** | `no logging host` などを誤って入れない |
| `hidekeys` を忘れない | 「except passwords」の文言が要件 |
| `ospf lsa` のみ指定 | `ospf` だけではなく `lsa` サブキーワードまで必要 |
| `notify syslog` と `logging enable` は両方必要 | 片方だけでは不完全 |


