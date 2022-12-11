FROM base AS parser

WORKDIR /

ENV config_file="/app/config.yaml"

COPY ./app/parser/ /app/parser
COPY ./app/common /app/common/
COPY ./configs/parser.yaml /app/config.yaml

EXPOSE 5001

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "-m", "uvicorn", "app.parser.app:app", "--host", "0.0.0.0", "--port", "5001" ]
