#! /bin/bash
nc -u -l localhost 42421 | aplay -r 9600 -f FLOAT_LE
