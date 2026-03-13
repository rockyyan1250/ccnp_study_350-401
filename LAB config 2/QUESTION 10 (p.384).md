# QUESTION 10

Tasks:
Troubleshoot R-WEST to achieve the desired results:

1. The locally generated logs should have sequence numbers, date and time.
2. The SNMP traps related to OSPF and participating interface state changes utilizing RFC1253-MIB OSPFv2 should be send to SNMP server.

***

## Topology と前提

- R-WEST ルータがキャンパスの西側にあり、その下に DSW-1 / ASW-NM / Syslog / SNMP などが接続された監視ネットワーク。
- この問題では、**R-WEST からのログ出力形式** と **OSPF/インターフェース状態の SNMP Trap** の設定だけが問われます。[^1]

***

## タスク文の翻訳と意味

1. 「ローカルで生成されるログメッセージに **シーケンス番号** と **日付・時刻** を付けなさい。」
→ コンソール／バッファ／Syslog に出るメッセージの頭に `[^000001] *Apr 28 10:10:00.391` のような情報を表示させる。[^1]

2. 「RFC1253-MIB OSPFv2 に基づき、OSPF と該当インターフェースの状態変化に関する SNMP Trap を SNMP サーバへ送信しなさい。」
→ OSPF ネイバー/インターフェースの up/down を Trap で送る設定（`snmp-server enable traps ospf state-change if-state-change`）を有効にする。[^1]

***

## 作業前に確認すべき設定と理由

R-WEST で以下を確認します。

1. `show run | include service`
    - 既に `service sequence-numbers` や `service timestamps log ...` が入っていないか確認。二重設定を避けるため。
2. `show run | section snmp`
    - 既に `snmp-server community` / `snmp-server host` など SNMP サーバの設定がされているか確認。
    - Trap を有効にするには送信先 SNMP サーバが事前定義されている必要があるので、その存在を確認する。[^1]
3. `show clock`
    - 時刻が正しそうかをざっと確認。タスクでは NTP まで求められていないが、Timestamp を付けたあとに検証するときの参考になる。

***

## 使用LAB

この問題も **General LAB** で R1 を R-WEST と見立てるのが扱いやすいです。[^2]

***

## Pre-setting（事前設定コマンド）

簡単に SNMP/Syslog の送信先だけ作っておきます。

```
enable
configure terminal
hostname R-WEST
logging host 10.1.100.14
snmp-server community public RO
snmp-server host 10.2.100.161 public
end
copy run start
```


***

## Task別 正解コマンドと解説


***

### ✅ Task 1：ローカルログにシーケンス番号・日付時刻を付加

**R-WEST**

```
enable
configure terminal
service sequence-numbers
service timestamps log datetime
end
copy run start
```

**解説：**

- `service sequence-numbers`
    - 全てのログメッセージ（`%SYS-5-CONFIG_I` など）に連番を付ける。トラブルシュートでメッセージの順序を追いやすくなる。[^1]
- `service timestamps log datetime`
    - ログに「年月日＋時刻」のタイムスタンプを付与。
    - 問題は「debugメッセージ」やローカルタイムまで要求していないので、`debug` や `localtime` オプションは不要。[^1]

***

### ✅ Task 2：OSPF インターフェース状態変化の SNMP Trap を有効化

**R-WEST**

```
enable
configure terminal
snmp-server enable traps ospf state-change if-state-change
end
copy run start
```

**解説：**

- `snmp-server enable traps ospf` が OSPF 関連 Trap 全般。
- `state-change` で「状態変化」に関する Trap サブカテゴリを選び、さらに
    - `if-state-change` で「物理/論理インターフェースの up/down」を対象にする。
- これにより、OSPF が有効なインターフェースの状態が変わると、OSPFv2 RFC1253-MIB に基づく Trap が SNMP サーバへ送信される。[^1]

***

## 検証コマンドと確認ポイント

### 1. ログフォーマットの確認

```
configure terminal
exit
```

直後にコンソール／`show logging` を見ると：

- 行頭に `000001:` のような **シーケンス番号** が付いているか。
- その後に `*Apr 28 10:10:00.391:` のような **日付・時刻** が表示されているか確認する。[^1]


### 2. SNMP Trap 設定の確認

```
show running-config | include snmp-server enable traps ospf
```

- `snmp-server enable traps ospf state-change if-state-change` が入っていることを確認。


### 3. Trap 送信の動作確認（概念的）

実機では SNMP サーバ側での確認が必要ですが、ルータ側からは以下を行う。

```
interface <OSPFが有効なインターフェース>
 shutdown
 no shutdown
```

- その直後に `show logging` を見ると、OSPF インターフェース down/up に関するログが出ている。
- SNMP サーバが正しく設定されていれば、そのタイミングで OSPF Trap も送信されていると判断できる。

***

このタイプの問題はコマンド自体は短いですが、「service」「snmp-server enable traps ospf state-change if-state-change」というフル構文を瞬時に思い出せるかがポイントです。

ここまでの説明で、特に覚えにくそう・混同しそうな部分はどこですか？
<span style="display:none">[^3]</span>

<div align="center">⁂</div>

[^1]: 300-410-685-25.pdf

[^2]: image.jpg

[^3]: image.jpg

