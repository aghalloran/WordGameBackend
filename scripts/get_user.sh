#!/bin/bash
curl -H "Accept: application/json" \
     "http://localhost:8080/wordgame/api/v1/players/1/" \
     > data_user.txt

cat data_user.txt | python -mjson.tool > pretty_data_user.txt
cat header.txt
