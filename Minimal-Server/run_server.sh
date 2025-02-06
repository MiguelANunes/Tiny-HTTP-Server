#!/bin/bash

if [ "$#" -eq 1 ]; then
	python3.11 Main.py $1
elif [ "$#" -eq 2 ]; then
	python3.11 Main.py $1 $2
else
	python3.11 Main.py
fi
