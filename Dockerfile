FROM python:3.7
RUN apt update && apt -y install gettext-base
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ARG PROCESS_TYPE
ENV PROCESS_TYPE ${PROCESS_TYPE}
CMD ["sh", "-c", "/run.sh $PROCESS_TYPE"]