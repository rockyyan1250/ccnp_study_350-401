# QUESTION 23

Tasks:
Task 1
An engineer is tasked to send system logging messages to SNMP and SYSLOG servers to meet the requirements below, but the results are not achieved.
Troubleshoot the configuration to meet the desired settings.
• R2 logs informational messages in sequence with the date and time to the IPv6 Syslog server, and duplicates the same messages to the SNMP server by using
version 2C and community string RO. Enable SNMP traps for syslog.
• SW2 logs system messages to a local buffer and duplicates the same messages to the SNMP server (SYSLOG server should not be enabled). Disable logging to
console and terminal.
Task 2
R1 sends traps for IPv6 OSPFv3 neighbor state and state changes to the SNMP server's IPv6 Address 2001:ABCD:ABCD:5678:A8BB:CCFF:FE00:200 using e0/0 as
the source, version 2C and community string RO, and logs system messages (severity informational) to the Syslog server IPv6 address
2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200.

QUESTION 23 は「IPv6 Syslog + SNMP traps」を R1/R2/SW2 で正しく組む問題です。

***

## 要件の整理

- Syslog サーバ IPv6: `2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200`
- SNMP サーバ IPv6: `2001:ABCD:ABCD:5678:A8BB:CCFF:FE00:200`[^1]


### Task 1

- **R2**
    - 情報レベルのログを「日時入り」で Syslog サーバへ送信。
    - 同じメッセージを SNMP サーバにも複製（SNMPv2c, community RO）。
    - `snmp-server enable traps syslog` 必要。
- **SW2**
    - ログはローカルバッファに保存。
    - 同じメッセージを SNMP サーバにも複製。
    - Syslog サーバへの送信は禁止。
    - console / monitor へのログ出力を無効化。


### Task 2

- **R1**
    - OSPFv3 の neighbor/state 変化の SNMP trap を、SNMP サーバ IPv6 宛てに e0/0 をソースにして送付（v2c, RO は既に設定済）。
    - 情報レベルの syslog を Syslog サーバ IPv6 に送る。

***

## 必要な修正コマンド

### 1) R1 の設定（Task 2）

```plaintext
enable
configure terminal
snmp-server enable traps ospfv3 state-change neighbor-state-change
snmp-server trap-source e0/0
logging trap informational
logging host ipv6 2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200
end
copy run start
```

- OSPFv3 の state / neighbor-state 変化トラップを有効化。
- trap の送信元 IP を e0/0 の IPv6 に固定。
- `logging trap informational` で info 以上を外部へ。
- Syslog サーバ IPv6 を `logging host ipv6` で指定。[^1]

***

### 2) R2 の設定（Task 1 Part 1）

```plaintext
enable
configure terminal
service timestamps log datetime
no logging host ipv6 FE80::250:79FF:FE66:682E
logging host ipv6 2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200
logging trap informational
snmp-server enable traps syslog
no snmp-server host 2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200 RO
snmp-server host 2001:ABCD:ABCD:5678:A8BB:CCFF:FE00:200 version 2c RO
end
copy run start
```

- `service timestamps log datetime` でログに日時を付与。
- 間違ったリンクローカルアドレスへの logging host を削除し、正しい Syslog サーバ IPv6 を追加。
- `logging trap informational` で info レベルを送る。
- `snmp-server enable traps syslog` で syslog メッセージを SNMP trap としても送信。
- 間違って Syslog サーバを SNMP host として登録しているエントリを削除し、正しい SNMP サーバ IPv6 + v2c/RO を再設定。[^1]

***

### 3) SW2 の設定（Task 1 Part 2）

```plaintext
enable
configure terminal
snmp-server enable traps syslog
no snmp-server host 2001:ABCD:ABCD:1234:A8BB:CCFF:FE00:200 RO
no logging trap
no logging console
no logging monitor
end
copy run start
```

- `snmp-server enable traps syslog` でローカルログを SNMP trap にも出す。
- Syslog サーバ宛の SNMP host 定義を削除し、SNMP サーバ宛の v2c 定義だけ残す。
- `no logging trap` で Syslog サーバへの送出を停止。
- `no logging console` / `no logging monitor` でコンソール／VTY へのログをオフにし、ローカルバッファのみ残す。[^1]

***

## 検証のポイント

- `show logging`
    - R2 で Syslog host が 2001:ABCD:ABCD:1234:... のみ、SW2 では logging buffered のみ有効で trap/console/monitor 無効になっていること。
- `show snmp host`
    - 各装置で SNMP サーバ IPv6 が 2001:ABCD:ABCD:5678:... で v2c/RO になっていること。
- OSPFv3 の隣接を flap させて、SNMP サーバ側で trap 受信と Syslog メッセージを確認。

SNMP と Syslog の連携で、いま一番混乱しやすいのは「どこで enable traps syslog が必要か」それとも「logging trap informational の役割」どちらですか？
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

