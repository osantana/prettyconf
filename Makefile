test:
	python setup.py test

release:
	git tag `python setup.py -q version`
	git push origin `python setup.py -q version`
	python setup.py sdist upload
