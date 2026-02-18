.PHONY: test publish deploy

test:
	python3 -m pytest -q

publish:
	echo "$$CI_REGISTRY_PASSWORD" | docker login -u "$$CI_REGISTRY_USER" --password-stdin "brooks.mc.umt.edu:5005"
	docker build -t "brooks.mc.umt.edu:5005/2026group1/sharespace:latest" .
	docker push "brooks.mc.umt.edu:5005/2026group1/sharespace:latest"

deploy:
	ssh -o StrictHostKeyChecking=no "$$SSH_USER@$$SSH_HOST" "echo '$$CI_REGISTRY_PASSWORD' | docker login -u '$$CI_REGISTRY_USER' --password-stdin 'brooks.mc.umt.edu:5005' && docker pull 'brooks.mc.umt.edu:5005/2026group1/sharespace:latest' && (docker rm -f sharespace || true) && docker run -d --name sharespace -p 80:8000 -v /srv/sharespace:/srv/sharespace 'brooks.mc.umt.edu:5005/2026group1/sharespace:latest'"
