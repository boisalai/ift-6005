#!/bin/bash
clear
git add .
# git commit -m "${1:-update}" -n
git commit -m "${1:-update}"
git push -u origin main
