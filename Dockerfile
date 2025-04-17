#pour torch cpu
#FROM python:3.9-slim
#pour cuda
FROM nvidia/cuda:12.8.1-cudnn-runtime-ubuntu22.04
#ffmpeg pour les fichers audio (tout fichier supporte par ffmpeg)
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*

#install py et pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python2 \
    python2-dev \
    python3.10 \
    python3.10-dev \
    python3.10-distutils \
    python3-pip \
    build-essential \
    pkg-config \
    libssl-dev \
    libpq-dev \
    libgl1-mesa-glx \
    curl \
    cmake \
    git \
    ninja-build && \
    rm -rf /var/lib/apt/lists/*

# Install Rust if needed cas de python slim.
#RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
#ENV PATH="/root/.cargo/bin:$PATH"

RUN python3.10 -m pip install --upgrade \
    "pip<24.1" \
    "setuptools>=67" \
    "packaging>=23" \
    wheel
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install pytest httpx

EXPOSE 80
#uncomment pour cas pas de docker compose
#Attention, necessite rebuild en cas de cha,gement de code.
#CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]