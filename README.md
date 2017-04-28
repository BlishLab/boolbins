## Installation

Open a terminal window. Navigate to the directory where you want this code to go.
If you're not sure what this means: the terminal is a [command line interface](https://en.wikipedia.org/wiki/Command-line_interface) that allows you to interact with the computer by typing commands. Here is a [list of commonly used commands](https://en.wikipedia.org/wiki/List_of_Unix_commands). Hint: start by typing cd followed by the filepath of the directory where you have your data.

Next, type  

```
git clone https://github.com/BlishLab/boolbins.git
cd boolbins
```

## Usage

Make sure the program is running correctly by typing `python boolbins.py -h` at the terminal. When you do this, you should see the following:

```
usage: boolbins.py [-h] -t THRESHOLDS [-o OUTPUT] [-v] [-l LIMIT]
                   [-d DIVERSITY]
                   file [file ...]

Performs boolean gating on flow cytometry data

positional arguments:
  file                  Files or directories to process

optional arguments:
  -h, --help            show this help message and exit
  -t THRESHOLDS, --thresholds THRESHOLDS
                        File with the thresholds to use for each antibody. See
                        readme for instructions on formatting this file.
  -o OUTPUT, --output OUTPUT
                        File to output the data to
  -v, --verbose         Show debug logging
  -l LIMIT, --limit LIMIT
                        Process the first `limit` lines of each file, 0
                        (default) for all of them.
  -d DIVERSITY, --diversity DIVERSITY
                        If given, output diversity scores to this file

```

This message is explaining the five inputs used by the program:
- A path to the directory where you have stored your text files
- A user-specified thresholds file showing your chosen thresholds (gates) for each marker
- A designated name for the output file where you want your results (must end in .csv)
- An optional cell number limit that tells the program how many cells to analyze per file
- An optional name for the output file where you want your diversity calculations (must end in .csv)

The program also takes an optional fourth input, ```-debug```, which can help you find where the code went wrong if anything misfires.

Before running the code, you need to create a file of your user-defined thresholds. The format for this file is:

1. First row: the EXACT headers from your data files
2. Second row: the thresholds over which you consider a cell positive for that marker
3. Third row: A "1" if that marker should be included in the analysis.

N.B.: Thresholds file must be the same format as your data files i.e. if data is CSV, thresholds is CSV. If data is tab delimited, thresholds is tab delimited.

You can also see the example file included if this is not clear.

You also need to export all of the data files you want to analyze into a folder somewhere on your computer. Your favorite flow cytometry analysis platform can do this for you. 

If you want to calculate the Inverse Simpson Index, an [ecological measure of diversity](https://en.wikipedia.org/wiki/Diversity_index), you can use the optional diversity input flag to specify where you want the additional diversity file to be written.

With these things in place, you can run the program. Type `python boolbins.py` at the command line, followed by your arguments. It doesn't matter what order the arguments are in. If you like, you can drag and drop the folder containing your text files right onto the terminal window to get it to print the path to that folder.

An example run might read: `python boolbins.py -thresholds myThresholds.csv my_text_files -output myResults.csv -limit 10000 -diversity myDiversity.csv`
