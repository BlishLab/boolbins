## Installation

Open a terminal window. Navigate to the directory where you want this code to go.

Next, type  

```
git clone https://github.com/BlishLab/boolbins.git
cd boolbins
```


## Usage

Make sure the program is running correctly by typing `python boolbins.py -h` at the terminal. When you do this, you should see the following:

```
usage: boolbins.py [-h] --thresholds THRESHOLDS [--output OUTPUT] [--debug]
                   [--limit LIMIT]
                   file [file ...]

Performs boolean gating on flow cytometry data

positional arguments:
  file                  Files or directories to process

optional arguments:
  -h, --help            show this help message and exit
  --thresholds THRESHOLDS
                        File with the thresholds to use for each antibody
  --output OUTPUT       File to output the data to
  --debug               Show debug logging
  --limit LIMIT         Process the first `limit` lines of each file, 0
                        (default) for all of them.

```

This message is explaining the four inputs required to the program:
- A user-specified thresholds file showing your chosen thresholds (gates) for each marker
- A designated name for the output file where you want your results (must end in .csv)
- An optional cell number limit that tells the program how many cells to analyze per file
- A path to the directory where you have stored your text files

The program also takes an optional fourth input, ```--debug```, which can help you find where the code went wrong if anything misfires.

Before running the code, you need to create a file of your user-defined thresholds. The format for this file is:

1. First row: the EXACT headers from your .txt files
2. Second row: the thresholds over which you consider a cell positive for that marker
3. Third row: A "1" if that marker should be included in the analysis.

You can also see the example file included if this is not clear.

You also need to export all of the .txt files you want to analyze into a folder somewhere on your computer. Your favorite flow cytometry analysis platform can do this for you. 

With these things in place, you can run the program. Type `python boolbins.py` at the command line, followed by your arguments. It doesn't matter what order the arguments are in. If you like, you can drag and drop the folder containing your text files right onto the terminal window to get it to print the path to that folder.

An example run might read: `python boolbins.py --thresholds myThresholds.csv my_text_files --output myResults.csv --limit 10000`
