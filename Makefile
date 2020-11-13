.PHONY: help init clean test validate mock create delete info deploy
.DEFAULT_GOAL := help
environment = "inlined"

help:
		@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init: ## init python
		@pipenv install --python /usr/bin/python3 --dev
		@pipenv run pip3 freeze --local

prod: ## prod python
		@rm -Rf .venv; PIPENV_VENV_IN_PROJECT=1 pipenv install --python /usr/bin/python3 
		@pipenv run pip3 freeze --local

clean: ## clean
		@pipenv --rm
		
delete: ## delete env
		@sceptre delete-env $(environment)

test: ## run the unit tests			
		
		#@pipenv run nosetests  -sv --with-xunit --xunit-file=nosetests.xml --with-xcoverage --xcoverage-file=coverage.xml --cover-package=modules
		@pipenv run pytest -vv --log-cli-level=INFO -p no:warnings