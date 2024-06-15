SHELL := /usr/bin/env bash

default:
	poetry install && \
	mkdir -p ~/.marvin/cli/assistants

install: default
	poetry run marvin assistant register -n "Customer Assistant" --overwrite src/app/assistants.py:customer_assistant

run: install
	poetry run marvin assistant chat -a "Customer Assistant" 2>/dev/null
