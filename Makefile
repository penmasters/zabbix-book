.PHONY: serve build validate preview translation-status translation-mark-reviewed

SOURCE_REF ?= HEAD

serve:
	ZABBIX_BOOK_DOCS_DIR=docs mkdocs serve

build:
	python3 tools/build_versioned_site.py \
		--repository . \
		--metadata .github/docs-versions.yml \
		--use-current-checkout \
		--output .build/site \
		--base-url http://localhost:8000/

validate:
	python3 tools/validate_versioned_site.py \
		.build/site --metadata .github/docs-versions.yml

preview:
	python3 -m http.server \
		--directory .build/site \
		-b 127.0.0.1 8000

translation-status:
ifdef LOCALE
	python3 tools/translation_status.py --locale "$(LOCALE)" --source-ref "$(SOURCE_REF)"
else
	python3 tools/translation_status.py --all --source-ref "$(SOURCE_REF)"
endif

translation-mark-reviewed:
	@test -n "$(LOCALE)" || (echo "LOCALE is required" >&2; exit 2)
	@test -n "$(PAGE)" || (echo "PAGE is required" >&2; exit 2)
	python3 tools/translation_status.py --locale "$(LOCALE)" --source-ref "$(SOURCE_REF)" --mark-reviewed "$(PAGE)"
