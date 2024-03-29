#FROM alephdata/memorious:latest
FROM alephdata/memorious:2.4.5
RUN apt-get update &&  apt-get install -y poppler-utils
COPY setup.py /crawlers/
COPY src /crawlers/src
RUN pip3 install -q -e /crawlers
COPY config /crawlers/config
COPY requirements.txt /crawlers
RUN pip3 install -r /crawlers/requirements.txt
ENV MEMORIOUS_BASE_PATH=/data \
    MEMORIOUS_CONFIG_PATH=/crawlers/config \
    MEMORIOUS_DEBUG=false \
    ARCHIVE_PATH=/data/archive \
    REDIS_URL=redis://redis:6379/0 \
    MEMORIOUS_DATASTORE_URI=postgresql://datastore:datastore@datastore/datastore \
