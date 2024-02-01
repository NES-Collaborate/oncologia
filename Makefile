server:
	@python -m flask run --debug

init-db:
	@python -m flask init-db

reset-db:
	@rm -rf instance
	@python -m flask init-db