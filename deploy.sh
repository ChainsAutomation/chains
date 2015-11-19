if [ -z "$DOCKER_EMAIL" ]; then
    echo "Not logging in to Docker Hub"
else
    docker login -e="$DOCKER_EMAIL" -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
    docker push chains/chains-master
fi
