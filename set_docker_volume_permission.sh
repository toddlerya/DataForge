#!/bin/bash

# 定义要处理的目录列表
directories=("data" "conf" "database" "logs")

# 遍历目录列表
for dir in "${directories[@]}"; do
  if [ -d "$dir" ]; then
    sudo chown -R 999:999 "$dir"
  fi
done
