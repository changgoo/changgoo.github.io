#!/bin/bash

cd CV/

# update bibliography
python get_pub.py
python pub2tex.py

# compile CV
pdflatex CV.tex
pdflatex CV.tex

# move files
cp CV.pdf ../

# cleanup
rm -rf *
git checkout .

# change dir
cd ../
