FROM python:alpine
WORKDIR /backend
ADD . /backend
RUN pip3 install -r requirements.txt
EXPOSE 5555
CMD ["python3", "app.py"]
