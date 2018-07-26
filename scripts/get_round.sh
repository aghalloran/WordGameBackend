#!/bin/bash
curl -H "Accept: application/json" \
     -D "header.txt" \
     "http://localhost:8080/wordgame/api/v1/rounds/2/?format=json" \
     > data_round.txt

cat data_round.txt | python -mjson.tool > pretty_data_round.txt
cat header.txt
