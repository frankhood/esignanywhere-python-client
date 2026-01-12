ARG PYTHON_VERSION=3.14

FROM python:${PYTHON_VERSION}-slim-bookworm

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8080

CMD ["bash"]