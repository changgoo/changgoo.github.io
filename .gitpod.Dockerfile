FROM gitpod/workspace-full

# Install custom tools, runtimes, etc.
# For example "bastet", a command-line tetris clone:
# RUN brew install bastet
#
# More information: https://www.gitpod.io/docs/config-docker/
# Install LaTeX
RUN sudo apt-get -q update && \
    sudo apt-get install -yq texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-generic-recommended \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-publishers && \
    sudo rm -rf /var/lib/apt/lists/*

# Install ads
RUN pip install -U ads
