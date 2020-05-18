SHELL := /bin/bash

.PHONY: all help prod-deploy

# target: all - Default target. Does nothing.
all:
	@echo "Hello $(LOGNAME), nothing to do by default"
	@echo "Try 'make help'"

# target: help - Display callable targets.
help:
	@egrep "^# target:" [Mm]akefile

# target: prod-deploy - Builds, (re)creates, and starts all prod containers (run this from prod VM).
prod-deploy:
	docker-compose up --detach --build