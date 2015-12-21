#!/bin/bash

USE_FORCE=0
TYPE="$1"
OS=$(uname -m)

if [ -z $TYPE ]; then
    TYPE="slave";
fi

if [[ $2 == --force* ]]; then
    USE_FORCE=1;
fi

if [ $OS = "x86_64" ]; then
    IMAGE="chains";
else
    IMAGE="rpi-chains";
fi

while true; do
    git fetch
    REMOTE_VERSION=`git rev-parse origin/master`
    LOCAL_VERSION=`git rev-parse HEAD`
    if [ $REMOTE_VERSION != $LOCAL_VERSION ] || [ $USE_FORCE -gt 0  ]; then
        git pull
        make test
        if [ "$?" -eq 0 ]; then
            ./bin/dockerfile-assemble.py $TYPE
            docker build --no-cache -t chains/$IMAGE-$TYPE . && docker push chains/$IMAGE-$TYPE
        else
            sleep 3600 # Tests failing waiting at least one hour before trying again
        fi
    fi;
    sleep 60;
done;
