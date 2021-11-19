# Unfortunately, alpine seems to have some problem with PyMupdf
# installed via pip
FROM python:3-slim-bullseye

WORKDIR /usr/src/greenpass

COPY requirements.txt ./
RUN apt-get update                          && \
    apt-get -y --no-install-recommends install \
	gcc=*                                  \
	libffi-dev=*                           \
	libzbar-dev=*                          \
	libc6-dev=*                            \
	libjpeg-dev=*                          \
	libmupdf-dev=*                      && \
    apt-get clean                           && \
    rm -rf /var/lib/apt/lists/*
RUN adduser python --disabled-password --disabled-login
USER python
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT [ "python", "greenpass.py" ]
CMD [ "--txt", "-" ]

