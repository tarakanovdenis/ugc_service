#!/bin/bash

python postgres_to_es/wait_for_es.py

python postgres_to_es/main.py
