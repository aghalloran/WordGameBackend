#!/bin/bash
curl -H "Accept: application/json" \
     -D "header.txt" \
     "http://localhost:8080/wordgame/api/v1/states/13/" \
     > data_state.txt

cat data_state.txt | python -mjson.tool > pretty_data_state.txt

cat header.txt
