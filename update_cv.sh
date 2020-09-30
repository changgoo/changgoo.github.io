#!/bin/bash

cd CV/

python get_pub.py
python pub2tex.py

pdflatex CV.tex
pdflatex CV.tex

cd ../

cp CV/CV.pdf .
