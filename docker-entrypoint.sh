#!/bin/sh

# The database container is ready and the schema has been applied.
# Now, run the Python script to populate the database with sample data.
python /app/database/creating_samples.py

uvicorn src.backend.main:app --host 0.0.0.0 --port 8000