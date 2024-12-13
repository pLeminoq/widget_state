#!/bin/bash

echo "Black:" &&
black --check widget_state tests &&
echo "" &&
# echo "MyPy:" &&
# mypy widget_state tests &&
# echo "" &&
echo "Flake8:" &&
flake8 --max-line-length 127 widget_state tests &&
echo "" &&
pytest

