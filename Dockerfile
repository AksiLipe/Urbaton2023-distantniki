FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PGPASSWORD=postgres

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get -y install postgresql-client-common && apt-get -y install postgresql-client

RUN pg_dump -U postgres -h host.docker.internal -p 5432 -d postgres > /app/backup_file.dump

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Run app.py when the container launches
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]