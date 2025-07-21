# Installing Graphviz and PyGraphviz

In order to use networkx write_dot function, you need to have Graphviz and PyGraphviz installed.

Check the installation instructions below for your operating system:

- https://pygraphviz.github.io/documentation/stable/install.html

## macOS

Following the instructions fo MacOS an error may occur:

```bash
brew install graphviz
pip install pygraphviz
````
If you encounter an error like this:

```bash
...
pygraphviz/graphviz_wrap.c:3023:10: fatal error: 'graphviz/cgraph.h' file not found
       3023 | #include "graphviz/cgraph.h"
            |          ^~~~~~~~~~~~~~~~~~~
Then you need to do retry the install with:

```bash
pip install --config-settings="--global-option=build_ext" \
            --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
            --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
            pygraphviz
```

