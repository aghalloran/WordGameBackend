#!/bin/bash
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X PUT \
     -d @pretty_data_state.txt \
     "http://localhost:8080/wordgame/api/v1/states/13/"

cat header.txt
