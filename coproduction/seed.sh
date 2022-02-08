#! /usr/bin/env bash

rm -rf /app/interlinkers-data || true
git clone https://github.com/interlink-project/interlinkers-data /app/interlinkers-data
python /app/app/initial_data.py
rm -rf /app/interlinkers-data || true