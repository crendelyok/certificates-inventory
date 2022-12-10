FROM base AS frontend

WORKDIR /

ENV config_file="/app/config.yaml"

COPY ./app/frontend/ /app/frontend
COPY ./app/common /app/common/
COPY ./config.yaml /app/

EXPOSE 5000

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "-m", "uvicorn", "app.frontend.app:app", "--host", "0.0.0.0", "--port", "5000" ]

