# Data Science for Business - Job market analysis

In this repository you will find an example of data cleaning and statistics focused on Job Market. 
In particular the analysis is based on dataset referring to the job market of the region Lombardia, Italy.

# Dataset Sources
- Regione Lombardia

More details are available in the Jupyter Notebook

# Requirements and how to run the code - Method 1 - Conda
In order to run this you simply need to install Python >= 3.6 and Anaconda. If you have already install Python on your PC you can simply run this command to install Anaconda:
    
    pip install conda

Otherwise you can find some other ways to instal Anaconda on its [official site](https://anaconda.com/). 
Once you have done with it you can create a Conda Virtual Environment containing all the necessary library using the following command:

    conda env create -f env.yml python=3.8 & conda activate dsfb

Then you can open the Jupyter Notebook in your browser running in your terminal

    jupyter-lab

# Requirements and how to run the code - Method 2 - Python venv
Creating virtual environments on MacOS or Linux:

	python3 -m venv path_to_new_virtual_environment

On Windows: 

	python -m venv path_to_new_virtual_environment

Start virtual environments on MacOS or Linux:

    source path_to_new_virtual_environment/bin/activate

On Windows:

    path_to_new_virtual_environment\Scripts\activate

Inside the enviroments run this command that will install all needed library:

    pip install -r requirements.txt

Then you can open the Jupyter Notebook in your browser running in your terminal

    jupyter-notebook

# Presentation Slides
In order to start the presentation install all requirements, and from the created environment run the following command:

    jupyter nbconvert 'Presentation Slides.ipynb' --to slides --post serve

# Dashboard
In order to start the presentation install all requirements, and from the created environments run the following command:

    streamlit run .\dashboard.py

