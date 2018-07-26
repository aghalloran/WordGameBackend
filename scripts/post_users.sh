#!/bin/bash
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X POST \
     -d @pretty_data_user_moe.txt \
     "http://localhost:8080/wordgame/api/v1/players/"

cat header.txt
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X POST \
     -d @pretty_data_user_larry.txt \
     "http://localhost:8080/wordgame/api/v1/players/"

cat header.txt
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X POST \
     -d @pretty_data_user_curly.txt \
     "http://localhost:8080/wordgame/api/v1/players/"

cat header.txt
