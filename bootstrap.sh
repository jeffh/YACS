#!/usr/bin/env sh
DIR=`dirname $0`

function setup(){
  cd "$DIR"
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
    echo "Commands: install|test"
    echo
    echo " install - Installs the application dependencies."
    echo " test - Installs the application and runs the tests."
    ;;
esac
