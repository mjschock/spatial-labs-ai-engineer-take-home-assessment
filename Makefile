SHELL := /usr/bin/env bash

default:
	poetry install

install:
	source .venv/bin/activate && \
		marvin assistant register --overwrite -n "Customer Assistant" src/app/assistants.py:customer_assistant

run:
	source .venv/bin/activate && \
		marvin assistant chat -a "Customer Assistant"
