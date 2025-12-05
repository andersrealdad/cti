FROM docker.io/n8nio/n8n:latest

USER root

RUN apk add --no-cache python3 py3-pip py3-requests py3-numpy py3-pandas \
    && PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --no-cache-dir --upgrade pip \
    && PIP_BREAK_SYSTEM_PACKAGES=1 pip3 install --no-cache-dir yfinance

USER node
