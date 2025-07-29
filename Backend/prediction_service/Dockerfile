FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    libtool \
    autoconf \
    automake \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/TA-Lib/ta-lib.git \
    && cd ta-lib \
    && ./configure --prefix=/usr \
    && make \
    && make install \
    && cd .. \
    && rm -rf ta-lib

RUN ldconfig
ENV LD_LIBRARY_PATH=/usr/lib:$LD_LIBRARY_PATH
ENV PKG_CONFIG_PATH=/usr/lib/pkgconfig:$PKG_CONFIG_PATH
ENV LDFLAGS=-L/usr/lib
RUN pip install --upgrade pip
RUN pip install --no-cache-dir numpy==1.24.4 \
    && pip install --no-cache-dir git+https://github.com/TA-Lib/ta-lib-python.git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
RUN mkdir -p /app/models
RUN python src/manage.py collectstatic --noinput
CMD ["gunicorn", "--bind", "0.0.0.0:8007", "prediction.wsgi:application"]