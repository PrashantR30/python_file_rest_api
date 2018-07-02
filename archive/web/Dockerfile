FROM ubuntu:latest
MAINTAINER Prashant Ramhit "https://github.com/PrashantR30" 
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install flask flask_httpauth
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
