# GRA-Fall-2020

## Convert RTF files to text

The process_documents.py tool returns a tab-delimited table file with the document ID, date, time, and article text as 
columns. 

It runs as a command line tool, so in the command line you just run the line below to do the conversion:

    python process_documents.py --input_dir "input/directory/path" --output_dir "output/directory/path"

You will need to change 2 arguments, input_dir and output_dir:

    --input_dir INPUT_DIR
        path to folder containing .RTF files.
    
    --output_dir OUTPUT_DIR
        path to folder to save delimited output.
 
 Run `python process_documents.py --help` for more options.
