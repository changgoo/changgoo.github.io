#!/bin/bash

cd CV/

# update bibliography
python get_pub.py
python pub2tex.py

# compile CV
pdflatex CV.tex
pdflatex CV.tex

# cleanup
rm -rf *
git checkout .

# move files
cd ../
cp CV/CV.pdf .
