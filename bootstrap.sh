#!/usr/bin/env bash
DIR=`dirname $0`
cd "$DIR"

function setup(){
  mkdir -p logs
  pip install -r requirements/development.txt
}

function runtest(){
  fab test
}

case "$1" in
  install)
    setup
    ;;
  test)
    setup
    runtest
    ;;
  *)
    echo "Commands:"
    echo
    echo " install - Installs the application dependencies."
    echo " test    - Installs the application and runs the tests."
    ;;
esac
