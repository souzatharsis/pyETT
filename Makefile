init:
	pip3 install -r requirements.txt
    
doc-gen:
	sphinx-apidoc -f -o ./docs/source ./pyETT
	(cd ./docs && make html)
	
publish:
	twine upload dist/*
