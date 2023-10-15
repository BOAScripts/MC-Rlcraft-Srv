#!/bin/bash

/usr/local/bin/mcrcon -H localhost -P 25575 -p -REDACTED- stop
while kill -0 $MAINPID 2>/dev/null
do
  sleep 0.5
done