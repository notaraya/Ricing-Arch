#!/usr/bin/env bash

pkill -x waybar
sleep 0.3
waybar >/dev/null 2>&1 &
