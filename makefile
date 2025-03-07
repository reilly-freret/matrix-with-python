# Makefile

define bail_if_already_running
	if [ -f .pid ]; then \
		echo "process already running"; \
		exit 1; \
	fi
endef

start:
	@echo "Starting background process..."
	@$(call bail_if_already_running)
	@sudo python main.py -a weather & echo $$! > ".pid"

quiet_start:
	@echo "Starting background process..."
	@$(call bail_if_already_running)
	@sudo python main.py -a weather > /dev/null 2>&1 & echo $$! > ".pid"

# Target to read the PID from pid.txt and kill the process
stop:
	@echo "Stopping background process..."
	@if [ -f .pid ]; then \
		kill `cat .pid`; \
		rm ".pid"; \
	else \
		echo ".pid file not found"; \
	fi
