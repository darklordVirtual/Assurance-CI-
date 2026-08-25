.PHONY: validate

validate:
	python3 scripts/validate_repository.py
	sha256sum --check checksums/SHA256SUMS
