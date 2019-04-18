#!/bin/bash

# Let's get your name for Git
echo "Enter your name for Git"

read input0

# Setting Git global user name
git config --global user.name "$input0"

# Let's get your email for Git
echo "Enter your email for Git"

read input1

# Setting Git global email
git config --global user.email "$input1"

# Tell me your editor
echo "What editor do you prefer?"
echo "geany, leafpad, notepadqq, etc."

read input2

# Setting editor
git config --global core.editor "$input2"

echo "Git global user info set!"
