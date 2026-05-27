.PHONY: test validate sast

test:
	@bash tests/run-tests.sh

validate:
	@claude plugin validate .claude-plugin/marketplace.json

sast:
	@bash scripts/sast.sh
