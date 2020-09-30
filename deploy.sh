#!/bin/bash
if [ -n "$GH_TOKEN" ]; then
    cd $TRAVIS_BUILD_DIR
    git checkout master
    mkdir pdf/
    mv CV.pdf pdf/CV.pdf
    git add -f pdf/CV.pdf
    git -c user.name='travis' -c user.email='travis' commit -m "current pdf"
    git push -q -f https://$GITHUB_USER:$GH_TOKEN@github.com/$TRAVIS_REPO_SLUG master
fi
