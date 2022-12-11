FROM base AS parser

WORKDIR /

ENV config_file="/app/config.yaml"

# RUN [ "mkdir", "-p", "/app/" ]

COPY ./app/parser/ /app/parser
COPY ./app/common /app/common/
COPY ./config.yaml /app/

EXPOSE 5001

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "-m", "uvicorn", "app.parser.app:app", "--host", "0.0.0.0", "--port", "5001" ]
