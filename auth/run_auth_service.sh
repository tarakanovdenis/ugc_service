#!/bin/bash

# Apply migrations
alembic upgrade head

# Start service
python -m main