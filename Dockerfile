FROM python:3.6

# Set the GOOGLE_APPLICATION_CREDENTIALS environment variable.
# At run time, /credentials must be binded to a volume containing a valid
# Service Account credentials file named datacatalog-tag-manager.json.
ENV GOOGLE_APPLICATION_CREDENTIALS=/credentials/datacatalog-tag-manager.json

# Install static code quality assurance tools.
RUN pip install flake8 yapf

WORKDIR /app

# Copy project files (see .dockerignore).
COPY . .

# Run static code quality assurance checks.
RUN yapf --diff --recursive src tests
RUN flake8 src tests

# Run the unit tests.
RUN python setup.py test

# Install the package.
RUN pip install .

ENTRYPOINT ["datacatalog-tag-manager"]
