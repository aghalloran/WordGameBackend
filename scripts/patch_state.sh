#!/bin/bash
curl -H "Content-Type: application/json" \
     -D "header.txt" \
     -X PATCH \
     -d @pretty_data_patch_state.txt \
     "http://localhost:8080/wordgame/api/v1/states/2/"

cat header.txt
