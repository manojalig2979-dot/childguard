@echo off
title ChildGuard AI - Live Android Child Agent Daemon
cd /d "%~dp0"
python simulator/run_android_agent.py
pause
