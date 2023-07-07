FROM python:3.9.6

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY main.py /
COPY assets /assets
COPY src /src

CMD ["python", "main.py"]