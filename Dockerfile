FROM python:3.12.5-bookworm

WORKDIR /

ENV GITLAB_ACCESS_TOKEN=GITLAB_ACCESS_TOKEN

# install necessary packages
# hadolint ignore=DL3008
RUN set -eux; \
  apt-get update && \
  apt-get install -y --no-install-recommends \
  python3 \
  python3-pip \
  python3-setuptools && \
  apt-get clean all && \
  rm -rf /var/lib/apt/lists/*

# install python packages from our requirements.txt
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# copy and execute repo_scanner.py
COPY linting_scanner.py .
COPY templates ./templates/.
ENTRYPOINT ["python3", "linting_scanner.py"]
