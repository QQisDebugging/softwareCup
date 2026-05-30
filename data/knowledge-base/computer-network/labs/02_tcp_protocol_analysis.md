# 实验二 TCP 协议分析

## 实验来源

- 本地参考文件：`D:\实验2TCP协议分析.pdf`
- 对应章节：第六章 传输层，第七章 应用层
- 对应知识点：TCP报文段、三次握手、序号、确认号、流量控制、拥塞控制、RTT、吞吐率、HTTP POST

## 实验目的

- 掌握 TCP 协议报文段格式。
- 理解 TCP 序号、确认号和连接建立过程。
- 分析 TCP 流量控制和拥塞控制现象。
- 使用 Wireshark 分析 TCP 性能，包括吞吐量和往返时间 RTT。

## 实验环境

- Windows
- Wireshark
- 浏览器

## 实验注意事项

- 实验过程中不要运行 VPN。
- 浏览器不要默认使用 HTTP/3 或 QUIC 协议通信，否则抓包结果可能无法体现传统 TCP/HTTP 行为。

## 实验步骤

### 1. 捕获本地主机到远程服务器的 TCP 分组

1. 在浏览器访问 `http://gaia.cs.umass.edu/wireshark-labs/alice.txt`，将 `alice.txt` 保存到本地。
2. 打开 `http://gaia.cs.umass.edu/wireshark-labs/TCP-wireshark-file1.html`。
3. 在网页中选择本地 `alice.txt` 文件，但暂时不要点击上传。
4. 启动 Wireshark 并开始抓包。
5. 回到浏览器点击 `Upload`，将文件上传到 `gaia.cs.umass.edu`。
6. 上传成功后停止抓包。

### 2. 查看抓包信息

在 Wireshark 显示过滤器中输入：

```text
tcp
```

观察本地主机和服务器之间的 TCP 与 HTTP 消息，包括三次握手、HTTP POST、数据段、Continuation 报文和 ACK。

### 3. 分析 TCP 基础机制

定位以下内容：

- 客户端 IP 地址和 TCP 端口号
- 服务器 IP 地址和 TCP 端口号
- TCP 三次握手中的 SYN、ACK 标志位
- raw sequence number
- raw acknowledgement number
- 包含 HTTP POST 的 TCP 报文段
- 前 4 个承载数据的 TCP 段
- 接收窗口字段

### 4. 分析 TCP 拥塞控制

在 Wireshark 中选择一个 TCP 报文段，打开：

```text
统计 -> TCP 流图 -> 时间序列
```

观察客户端向服务器发送的 TCP 段序号与发送时间之间的关系，分析慢启动、拥塞避免、重传和窗口变化。

## 实验任务

完成以下问题，并附实验步骤和截图：

1. 向 `gaia.cs.umass.edu` 服务器传送文件的客户端主机 IP 地址和 TCP 端口号分别是多少？附本机 IP 地址、MAC 地址截图或 `ipconfig` 结果。
2. `gaia.cs.umass.edu` 服务器的 IP 地址是多少？此次连接中服务器发送和接收 TCP 报文的端口号是多少？
3. 给出 TCP 三次握手过程，说明 SYN、ACK 标志位设置，以及 raw 序号和 raw 确认号。
4. 包含 HTTP POST 命令头的 TCP 报文段序号是多少？该 TCP 段有效载荷部分包含多少字节数据？
5. 如果将包含 HTTP POST 消息的 TCP 报文段看作连接上的第一个数据段，计算前两个数据段的发送时间、ACK 接收时间和 RTT；在计算第二个段 ACK 后的 EstimatedRTT 时，令初始 EstimatedRTT 等于第一个段测量 RTT，取 `alpha=0.125`。
6. 前 4 个承载数据的 TCP 段，每个段长度是多少？
7. 前 4 个承载数据 TCP 段发送过程中，服务器向客户端通告的窗口最小值是多少？该窗口值有什么作用？
8. 判断发送过程中是否存在重传报文段，并说明依据。
9. 计算 TCP 连接吞吐率，给出计算过程。
10. 结合 TCP 时间序列图，分析是否能辨别慢启动阶段的起止、何处转入拥塞避免阶段，以及实际窗口变化与理论拥塞控制算法的差异。

## 计算提示

EstimatedRTT 可按教材常用公式计算：

```text
EstimatedRTT = (1 - alpha) * EstimatedRTT + alpha * SampleRTT
```

吞吐率可按以下思路估算：

```text
吞吐率 = 传输字节数 / 传输耗时
```

实际计算时需要说明选取了哪些 TCP 段、起止时间和字节范围。

## 实验报告要求

- 本机网络参数截图或记录
- Wireshark 抓包文件或关键截图
- 三次握手分析表
- HTTP POST 报文段分析
- RTT 与 EstimatedRTT 计算过程
- 前 4 个数据段长度和接收窗口分析
- 重传判断依据
- 吞吐率计算过程
- TCP 时间序列图及拥塞控制分析

## 常见错误

- 使用了 VPN 或 HTTP/3/QUIC，导致抓不到预期 TCP/HTTP 流。
- 没有切换到 raw sequence number 和 raw acknowledgement number。
- 把接收窗口当成拥塞窗口。
- RTT 起止报文对应关系选错。
- 只给出截图，没有解释字段含义和计算过程。
