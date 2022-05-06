FROM ubuntu:20.04
RUN apt-get update
RUN apt install software-properties-common -y
RUN apt-get install -y tesseract-ocr-eng \
    python3.9 \
    tesseract-ocr-rus \
    python3-pip
RUN apt-get clean
RUN apt-get autoremove

ADD logic /app/logic
ADD templates /app/templates
ADD static /app/static
ADD requirements.txt /app
ADD README.txt /app
ADD server.py /app

RUN pip3 install --upgrade pip
RUN pip3 install -r /app/requirements.txt

WORKDIR /app
CMD ["python3", "server.py"]
