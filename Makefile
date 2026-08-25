.PHONY: validate

validate:
	python3 scripts/validate_repository.py
	python3 -m unittest discover -s tests -v
	sha256sum --check checksums/SHA256SUMS
