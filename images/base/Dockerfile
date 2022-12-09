FROM ubuntu:22.04 AS base

RUN apt-get update  \
    && apt-get install -y --no-install-recommends   \
        python3=3.10*   \
        python3-pip=22.0.2* \
    && apt-get clean    \
    && rm -rd /var/lib/apt/lists/*

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt
