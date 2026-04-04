# watermark_dataset

## Project Overview
This project builds a watermark network traffic dataset covering time-based, sequence-based, and content-based watermarking methods. It outputs pcap files and feature datasets that can be used for analysis and model training.

The current workflow is local automated collection: run embedding scripts in sequence, capture traffic, and save pcaps into method-specific folders.

## Current Directory Structure
The following structure reflects the current repository layout:

```text
watermark_dataset/
├── auto_capturePcap.sh
├── extract_arriveT_ipd.py
├── processed_pcap.py
├── features_extractor.py
├── labelencoder.py
├── datasetsplitter.py
├── content-based/
│   ├── ip_based/
│   ├── tcp_based/
│   ├── http_based/
│   └── dns_based/
├── time-based/
│   ├── sibw/
│   │   ├── icmp/
│   │   └── ssh/
│   ├── hnfw/
│   │   ├── icmp/
│   │   └── ssh/
│   ├── eqnw/
│   │   ├── icmp/
│   │   └── ssh/
│   └── rldjw/
│       ├── icmp/
│       └── ssh/
├── sequence-based/
    ├── frw-trace/
    │   ├── icmp/
    │   └── ssh/
    └── hstw/
    │   ├── icmp/
    │   └── ssh/
        
```

## Collection Script

### auto_capturePcap.sh
What it does:
1. Runs embedding scripts in the order defined by `SCRIPT_ORDER`.
2. Runs each script for its own round count from `TOTAL_ITERATIONS_MAP`.
3. Captures traffic for `CAPTURE_DURATION` seconds per round.
4. Stops the current embedding process when the capture window ends.
5. Saves pcap files into the method-specific path defined in `PCAP_DIRS` (currently configured for ssh paths).

Key settings:
- `SCRIPT_ORDER`: execution order of methods.
- `TOTAL_ITERATIONS_MAP`: rounds per method.
- `PCAP_DIRS`: output directory mapping.
- `CAPTURE_INTERFACE`: network interface for tcpdump.
- `CAPTURE_DURATION`: capture time per round.

Run:

```bash
bash auto_capturePcap.sh
```

## Data Processing Scripts

### 1) Parse pcap into structured CSV
- Script: `processed_pcap.py`
- Input: `./raw_pcap`
- Output: `./processed_pcap/*.csv`

```bash
python3 processed_pcap.py
```

### 2) Extract arrival time and IPD sequences
- Script: `extract_arriveT_ipd.py`
- Purpose: extract arrival timestamps and inter-packet delays from pcap files.

```bash
python3 extract_arriveT_ipd.py
```

### 3) Extract statistical features
- Script: `features_extractor.py`
- Output: `./features/watermarking_features.csv`

```bash
python3 features_extractor.py
```

### 4) Encode labels
- Script: `labelencoder.py`
- Output: `./features/watermarking_features_with_labels.csv`

```bash
python3 labelencoder.py
```

### 5) Split train/test datasets
- Script: `datasetsplitter.py`
- Output: `./datasets/`

```bash
python3 datasetsplitter.py
```

## Recommended Environment

```bash
sudo apt update
sudo apt install -y python3 python3-pip tcpdump
pip3 install scapy pandas numpy scipy scikit-learn tqdm matplotlib
```

If embedding scripts use `netfilterqueue`, install the corresponding system dependencies for your Linux distribution.

## Notes
1. Capturing traffic and modifying iptables usually require root privileges.
2. `auto_capturePcap.sh` is long-running; use `tmux` or `screen`.
3. If you switch to ICMP collection, update both `PCAP_DIRS` and the matching embed script rules.
4. Label mapping in `labelencoder.py` is currently filename-keyword based; update mapping when adding new methods.

## Contact
If you have questions, contact: 2331121322@tiangong.edu.cn
