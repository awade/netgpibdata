#!/bin/bash

# In the event that matplotlib refuses to work properly add a file ~/.matplotlib to the home directory and add the following line "backend: TkAgg".

dir=$(pwd)
echo $dir

# Check if virtualenv install, install if necessary
if [  $(pip list | grep -ci "virtualenv") = 0 ]; then
	echo "virtualenv not installed, it is necessary installing with pip"
	pip install virtualenv
fi

# Make virtual environment
echo "$dir/env" 
if [ ! -d "$dir/env" ]; then
	echo "Making local env dir for python envoronment"
	virtualenv "$dir/env"
fi

# Switch to environment and perform install on necessary packages
if [ -d "$dir/env" ]; then
#	source env/bin/activate
	env/bin/pip install -r requirements.txt
else
	echo "Couldn't find env dir, are you located in root of repo?"
fi

echo "Script reached the end"



#env/bin/pip install -r requirements.txt
