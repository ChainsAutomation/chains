#!/bin/bash

mv /etc/chains/devices /etc/chains/services
sed -ie 's/device/service/g' /etc/chains/rules_available/*
