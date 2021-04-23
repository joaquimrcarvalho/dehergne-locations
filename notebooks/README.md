# Notebooks

This folder contains Jupyter notebooks that interact with the MHK/Timelink database to process data in forms not available using the web interface.

To be able to run notebooks you need to install the Python VSCode extension and a Python interpreter on the current machine.

## Install the Python instruction and the Python interpreter

To install the Python extension at https://marketplace.visualstudio.com/items?itemName=ms-python.python

## Install the SQL extension for notebooks

Open the terminal in VSCode: Command+j or menu `Terminal` -> `New terminal`

Type 

     pip install ipython-sql `[return]`

When finished install the Mysql connector


    pip install mysql-connector-python


## Install auxiliary packages

Type 

    pip install python-dotenv

when finish install data analysis package

    pip install pandas

## References

* https://pypi.org/project/ipython-sql/
* https://pypi.org/project/python-dotenv/
* https://pypi.org/project/mysql-connector-python/
* https://pandas.pydata.org