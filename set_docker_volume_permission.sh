#!/bin/bash

# 定义要处理的目录列表
directories=("data" "conf" "database" "logs", "caddy")

# 遍历目录列表
for dir in "${directories[@]}"; do
  if [ -d "$dir" ]; then
    sudo chown -R 1000:1000 "$dir"
  fi
done
