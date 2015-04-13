.PHONY: build clean

build: index.js

index.js: src/index.js
	jsx src/ .

clean:
	rm index.js
