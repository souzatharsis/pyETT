init:
	pip3 install -r requirements.txt

lint:
	black pyETT/*.py
	black tests/*.py
	mypy pyETT/*.py

test:
	python3 -m pytest
    
doc-gen:
	sphinx-apidoc -f -o ./docs/source ./pyETT
	(cd ./docs && make html)
	
publish:
	python3 -m build
	twine upload dist/*
