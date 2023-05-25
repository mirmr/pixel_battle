runserver:
	battlecli server run

install_prod:
	pip install .

install:
	pip install --editable .[dev]

stylecheck:
	black --diff pixel_battle

style:
	black pixel_battle

test:
	pytest -v pixel_battle/api
