#!/bin/bash
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X PUT \
     -d @pretty_data_round.txt \
     "http://localhost:8080/wordgame/api/v1/rounds/2/"

cat header.txt
