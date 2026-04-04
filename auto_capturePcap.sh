#!/bin/bash

# --- 本地配置 ---
# 按顺序执行的脚本标识
SCRIPT_ORDER=(EQNW HNFW SIBW rldjw frw hstw)

# 每个脚本各自执行的轮数
declare -A TOTAL_ITERATIONS_MAP=(
    [SIBW]=250
    [HNFW]=193
    [EQNW]=250
    [rldjw]=250
    [frw]=250
    [hstw]=250
)

# 轮数兜底值，防止新脚本未配置时脚本直接失败
DEFAULT_ITERATIONS=250

# 脚本路径配置
declare -A SCRIPT_PATHS=(
    [SIBW]="/root/lt_beacon_timeslot/experiment-e/embed_DICBW/embedv5_article2.py"
    [HNFW]="/root/beacon_timeslot/experiment-e/embed_study_empty_4bit/embedv1.py"
    [EQNW]="/root/beacon_timeslot/experiment-e/embed_empty_2bit/embed.py"
    [rldjw]="/root/iot-j_watermarking/embed_wm/embed_no_ai.py"
    [frw]="/root/multi_beacon/embed/embeddingv5.py"
    [hstw]="/root/iot-j_watermarking/other_nfw_methods/embed/hswt/hstw_embed_xuhuan.py"
)

# 不同脚本对应不同 pcap 输出目录
# declare -A PCAP_DIRS=(
#     [SIBW]="./time-based/sibw/icmp/"
#     [HNFW]="./time-based/hnfw/icmp/"
#     [EQNW]="./time-based/eqnw/icmp/"
#     [rldjw]="./time-based/rldjw/icmp/"
#     [frw]="./sequence-based/frw-trace/icmp/"
#     [hstw]="./sequence-based/hstw/icmp/"
# )
declare -A PCAP_DIRS=(
    [SIBW]="./time-based/sibw/ssh/"
    [HNFW]="./time-based/hnfw/ssh/"
    [EQNW]="./time-based/eqnw/ssh/"
    [rldjw]="./time-based/rldjw/ssh/"
    [frw]="./sequence-based/frw-trace/ssh/"
    [hstw]="./sequence-based/hstw/ssh/"
)
# 本地抓包网卡
CAPTURE_INTERFACE="ens224"

# 抓包时长 (秒)
CAPTURE_DURATION=30 # 30 秒

# 循环间隔 (秒) - 每次循环结束后等待的时间，防止过快执行
LOOP_INTERVAL=5

# 确保本地目录存在
for ACTIVE_SCRIPT in "${SCRIPT_ORDER[@]}"; do
    LOCAL_SCRIPT_PATH="${SCRIPT_PATHS[$ACTIVE_SCRIPT]}"
    AFTER_PCAP_DIR="${PCAP_DIRS[$ACTIVE_SCRIPT]}"
    TOTAL_ITERATIONS="${TOTAL_ITERATIONS_MAP[$ACTIVE_SCRIPT]:-$DEFAULT_ITERATIONS}"

    if [ -z "$LOCAL_SCRIPT_PATH" ] || [ -z "$AFTER_PCAP_DIR" ]; then
        echo "配置错误：ACTIVE_SCRIPT=$ACTIVE_SCRIPT 未定义路径或目录"
        exit 1
    fi

    mkdir -p "${AFTER_PCAP_DIR}"

    for ITERATION in $(seq 1 "$TOTAL_ITERATIONS"); do
        # 生成当前时间戳作为文件名的一部分
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        AFTER_PCAP_NAME="watermarked_${TIMESTAMP}.pcap"

        echo "==================================================="
        echo "--- 开始 ${ACTIVE_SCRIPT} 的第 ${ITERATION}/${TOTAL_ITERATIONS} 轮抓包和脚本执行 (${TIMESTAMP}) ---"
        echo "==================================================="
        echo "当前脚本标识: ${ACTIVE_SCRIPT}"
        echo "当前脚本路径: ${LOCAL_SCRIPT_PATH}"
        echo "当前 pcap 目录: ${AFTER_PCAP_DIR}"

        echo "--- 启动流量捕获 ---"

        # 在本地启动抓包：使用 timeout 控制时长，到时自动停止
        echo "在本地设备上启动 tcpdump (${AFTER_PCAP_NAME}) 到目录 ${AFTER_PCAP_DIR}..."
        sudo timeout "${CAPTURE_DURATION}" tcpdump -i "${CAPTURE_INTERFACE}" -w "${AFTER_PCAP_DIR}/${AFTER_PCAP_NAME}" &
        TCPDUMP_PID=$!

        # --- 随机延迟后执行本地脚本 ---
        RANDOM_DELAY=$(( RANDOM % 3 + 2 )) # 生成 2 到 4 秒的随机延迟
        echo "将会在 ${RANDOM_DELAY} 秒后，在本地执行 ${LOCAL_SCRIPT_PATH}..."
        sleep "$RANDOM_DELAY"

        # 在本地后台执行 Python 脚本
        echo "正在本地执行脚本..."
        python3 "${LOCAL_SCRIPT_PATH}" &
        SCRIPT_PID=$!

        # 继续等待剩余时间，确保本轮总时长不小于 CAPTURE_DURATION
        echo "等待剩余的抓包时间 (总时长 ${CAPTURE_DURATION} 秒)..."
        REMAINING_TIME=$(( CAPTURE_DURATION - RANDOM_DELAY ))
        if [ "$REMAINING_TIME" -gt 0 ]; then
            sleep "$REMAINING_TIME"
        fi

        # 抓包时间到后，确保 Python 脚本也停止
        if kill -0 "$SCRIPT_PID" 2>/dev/null; then
            echo "抓包时间已到，停止 Python 脚本 (${SCRIPT_PID})..."
            kill "$SCRIPT_PID" 2>/dev/null
            wait "$SCRIPT_PID" 2>/dev/null
        fi

        # 等待抓包进程结束（正常由 timeout 自动结束）
        wait "$TCPDUMP_PID" 2>/dev/null

        echo "--- 流程完成 ---"

        if [ "$ITERATION" -lt "$TOTAL_ITERATIONS" ]; then
            echo "--- 等待 ${LOOP_INTERVAL} 秒后开始下一轮循环 ---"
            sleep "$LOOP_INTERVAL"
        fi
    done
done