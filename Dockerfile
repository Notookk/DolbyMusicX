# FROM nikolaik/python-nodejs:python3.10-nodejs19

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends ffmpeg \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# COPY . /app/
# WORKDIR /app/
# RUN pip3 install --no-cache-dir -U -r requirements.txt

# CMD bash start


FROM nikolaik/python-nodejs:python3.10-nodejs19

# Use Debian archive for Buster
RUN sed -i 's/deb.debian.org\/debian/archive.debian.org\/debian/g' /etc/apt/sources.list \
    && sed -i '/security.debian.org/d' /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/
WORKDIR /app/
RUN pip3 install --no-cache-dir -U -r requirements.txt

CMD bash start
