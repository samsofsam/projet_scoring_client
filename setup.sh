#!/bin/bash

# Installer pyenv (si pyenv n'est pas déjà installé)
if ! command -v pyenv &> /dev/null
then
    echo "pyenv could not be found, installing..."
    curl https://pyenv.run | bash
fi

# Installer la version de Python souhaitée (par exemple, 3.8.10)
pyenv install 3.9.13

# Définir la version de Python comme version globale
pyenv global 3.9.13

# Vérifier que la version a bien été installée
python --version
