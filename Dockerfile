FROM python:3.7
WORKDIR /app

# Copy the credentials file and use it to set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
COPY ./credentials/*.json ./credentials/
ENV GOOGLE_APPLICATION_CREDENTIALS=./credentials/datacatalog-tag-manager.json

# Copy project files (see .dockerignore).
COPY . .

# Install the package and its dependencies.
RUN pip install .

# Run the unit tests.
RUN python setup.py test

ENTRYPOINT ["python", "main.py"]
