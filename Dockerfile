FROM python:3
COPY req.txt /
COPY marvel.py /
RUN pip install -r req.txt
RUN pip install --upgrade pip
CMD python marvel.py
