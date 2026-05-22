.PHONY: test validate

test:
	@bash tests/run-tests.sh

validate:
	@claude plugin validate .claude-plugin/marketplace.json
