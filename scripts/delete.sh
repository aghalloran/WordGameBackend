#!/bin/bash
curl -X DELETE \
     -D "header.txt" \
     "http://localhost:8080/wordgame/api/v1/rounds/1/"

cat header.txt
