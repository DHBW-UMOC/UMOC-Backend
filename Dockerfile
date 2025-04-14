FROM python:3.12-slim
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "src/main.py"]