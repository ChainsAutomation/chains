if [ -z "$DOCKER_EMAIL" ] || [ "$DEPLOY" == "false" ] || [ "$BUILD" == "false" ]; then
    echo "Not logging in to Docker Hub or decided not to deploy"
else
    docker login -e="$DOCKER_EMAIL" -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
    docker push chains/chains-master
fi
