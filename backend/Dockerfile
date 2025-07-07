# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container at /code
COPY ./app /code/app
COPY ./cli /code/cli
COPY ./test /code/test

COPY main.py /code/
COPY requirements.txt /code/
COPY pyproject.toml /code/

COPY .env /code/

RUN pip install -e .

ENV PYTHONPATH="/code:/code/app:/code/cli"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Run main.py when the container launches
CMD ["python", "main.py"]