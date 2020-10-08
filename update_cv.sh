#!/bin/bash

cd CV/

# update bibliography
python get_pubs.py
python pubs2tex.py

# compile CV
pdflatex -interaction=nonstopmode CV.tex
pdflatex -interaction=nonstopmode CV.tex

# change dir
cd ../

# move files
DIR=html

cp CV/CV.pdf $DIR/
