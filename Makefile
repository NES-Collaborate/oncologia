server:
	@python -m flask run --debug

init-db:
	@python -m flask init-db
	@python generate_default_values.py

reset-db:
	@rm -rf instance
	@make init-db

fake-db:
	@python generate_fake_data.py