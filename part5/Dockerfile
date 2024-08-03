FROM python:3.12-slim
RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
WORKDIR /code
COPY *.py /code/
ENTRYPOINT uvicorn entrypoints.main:app --reload --host 0.0.0.0 --port 8000
