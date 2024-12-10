FROM python:3.11-slim

WORKDIR /code

# Install poetry
RUN pip install poetry

# Copy configuration files
COPY pyproject.toml poetry.lock* pytest.ini ./

# Configure poetry to not create a virtual environment in the container
RUN poetry config virtualenvs.create false

# Install all dependencies including dev dependencies
RUN poetry install --no-interaction --no-ansi

# Copy application code and tests
COPY ./app /code/app
COPY ./tests /code/tests

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 