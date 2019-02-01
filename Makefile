test:
	python setup.py test

clean:
	-find . -iname "*.py[ocd]" -delete
	-find . -iname "__pycache__" -exec rm -rf {} \;
	-rm -rf dist

release: clean test
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	rm -rf dist/*
	python setup.py sdist
	twine check dist/*
	twine upload dist/*
