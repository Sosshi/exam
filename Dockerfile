
FROM python:3.9


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


WORKDIR /app


COPY requirements.txt /app/


RUN pip install --no-cache-dir -r requirements.txt


COPY . /app/


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]


EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
