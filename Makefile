clean:
	find . -name *.out -o -name *.aux -o -name *.log | xargs -n 1 rm
