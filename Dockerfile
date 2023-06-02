FROM python:3.10-alpine

WORKDIR /reports

COPY ./requirements.txt .

RUN apk add --no-cache postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    python -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY ./src /reports

ENTRYPOINT [ "python" ]

CMD [ "reports.py", "fetch", "github" ]