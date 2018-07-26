#!/bin/bash
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X POST \
     -d @pretty_data_round.txt \
     "http://localhost:8080/wordgame/api/v1/rounds/"

cat header.txt
