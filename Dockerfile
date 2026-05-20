FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 47780 47701 47702 47703

ENTRYPOINT ["python3", "-m", "src.api"]
CMD ["--port", "47780"]
