FROM python:3.11-slim

WORKDIR /notebooks

COPY requirements.txt .
COPY .env .env

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

RUN python -m ipykernel install --user --name=notebook-env --display-name "Python (Notebook Env)"

EXPOSE 9999

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=9999", "--allow-root", "--ServerApp.token=", "--ServerApp.password="]
