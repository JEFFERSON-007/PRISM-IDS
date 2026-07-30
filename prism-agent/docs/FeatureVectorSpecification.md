# Feature Vector Technical Specification

## Numerical Feature Fields

| Field Name | Type | Description | Mathematical Definition / Value |
|---|---|---|---|
| `duration` | Float | Active flow duration in seconds | $\text{end\_time} - \text{start\_time}$ |
| `total_packets` | Integer | Total packets in flow | $N_{\text{fwd}} + N_{\text{bwd}}$ |
| `forward_packets` | Integer | Packets sent from source to destination | $N_{\text{fwd}}$ |
| `backward_packets` | Integer | Packets sent from destination to source | $N_{\text{bwd}}$ |
| `total_bytes` | Integer | Total payload and header bytes | $B_{\text{fwd}} + B_{\text{bwd}}$ |
| `mean_pkt_len` | Float | Average packet length in bytes | $\mu = \frac{\sum B}{N}$ |
| `std_pkt_len` | Float | Standard deviation of packet length | $\sigma = \sqrt{\frac{\sum (x_i - \mu)^2}{N-1}}$ |
| `mean_iat` | Float | Average Inter-Arrival Time | $\text{duration} / (N - 1)$ |
| `packets_per_sec` | Float | Throughput in packets per second | $N / \text{duration}$ |
| `syn_ratio` | Float | Ratio of SYN packets | $N_{\text{syn}} / N$ |
| `direction_entropy`| Float | Shannon entropy of traffic direction | $-\sum p_d \log_2(p_d)$ |
