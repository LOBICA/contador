#!/bin/env bash

black . && isort . && flake8 .
