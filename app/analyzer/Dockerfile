FROM base AS analyzer

WORKDIR /
# VOLUME [ "/app/analyzer/db" ]

ENV config_file="/app/config.yaml"

COPY ./app/analyzer/ /app/analyzer
COPY ./app/common /app/common/
COPY ./configs/analyzer.yaml /app/config.yaml

EXPOSE 5002

ENTRYPOINT [ "/usr/bin/python3" ]
CMD [ "-m", "uvicorn", "app.analyzer.app:app", "--host", "0.0.0.0", "--port", "5002" ]
