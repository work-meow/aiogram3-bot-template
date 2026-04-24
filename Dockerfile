FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /src

COPY pyproject.toml ./

RUN uv sync --no-editable --no-cache

COPY . /src

EXPOSE 8080

CMD ["uv", "run", "python", "-m", "app"]