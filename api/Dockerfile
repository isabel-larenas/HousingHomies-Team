FROM python:3.11-slim

WORKDIR /apicode

COPY api/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ .

# ml-src is baked in at /ml-src and put on the path so the backend can
# import the ML modules (student_linreg, government_linreg) directly,
# keeping their source of truth in ml-src/ and out of the backend package.
# Mirrors the bind-mount + PYTHONPATH setup in docker-compose.yaml (dev).
COPY ml-src/ /ml-src/
ENV PYTHONPATH=/ml-src

EXPOSE 4000

# Run Python in unbuffered mode to ensure logs are immediately visible
CMD ["python", "-u", "backend_app.py"]
