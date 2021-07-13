FROM python:3

RUN useradd -ms /bin/bash python

USER python
ADD main.py /home/python
ADD rabbit.py /home/python
ADD query_processor.py /home/python
ADD run_query.py /home/python
ADD stopwords.txt /home/python
ADD requirements.txt /home/python
WORKDIR /home/python
RUN pip install -r requirements.txt

CMD ["host.docker.internal", "guest", "guest"]
ENTRYPOINT ["python", "main.py"]

