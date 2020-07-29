#!/usr/bin/env bash

set -eu

JAR=rabbit-groovy.jar
TARGET=../../../target/$JAR

if [[ ! -e $JAR ]] ; then
  if [[ ! -e $TARGET ]] ; then
    cd ../../../
    mvn package
    cd -
  fi
  echo "Copying JAR file."
  cp $TARGET ./
fi

if [[ -e $TARGET ]] && [[ $TARGET -nt $JAR ]] ; then
  echo "Copying JAR file."
  cp $TARGET .
fi

docker build -t rabbit-groovy .


