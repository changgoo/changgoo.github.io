#!/bin/bash

cd CV/

# update bibliography
python get_pubs.py
python pubs2tex.py

# compile CV
xelatex -interaction=nonstopmode CV.tex

# move files
cp CV.pdf ../

# cleanup
rm -rf *
git checkout .

# change dir
cd ../
