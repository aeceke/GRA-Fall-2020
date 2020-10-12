import argparse
import os
import sys
import glob
import re
from datetime import datetime
import pandas as pd
from striprtf.striprtf import rtf_to_text

# Create the parser
argparser = argparse.ArgumentParser()

# Add the arguments
argparser.add_argument(
    "--input_dir",
    help="path to folder containing .RTF files",
    action="store",
    type=str,
    required=True,
)
argparser.add_argument(
    "--output_dir",
    help="path to folder to save delimited output",
    action="store",
    type=str,
    default=".",
)
argparser.add_argument(
    "--delimiter",
    help="delimiter to separate entries in output",
    action="store",
    type=str,
    default="\t",
)

argparser.add_argument(
    "--document_id_pattern",
    "--docidpatt",
    help="regular expression pattern to find document ID",
    action="store",
    type=str,
    default=r"^Document \w{25}$",
)

argparser.add_argument(
    "--date_pattern",
    "--datepatt",
    help="regular expression pattern to find article dates",
    action="store",
    type=str,
    default="(\d{1,2}) (January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})",
)

argparser.add_argument(
    "--time_pattern",
    "--timepatt",
    help="regular expression pattern to find time",
    action="store",
    type=str,
    default=r"(\d{1,2}):(\d{2})",
)

argparser.add_argument(
    "--file_count",
    help="number of files to read",
    action="store",
    type=int,
    default=None,
)

# Execute the parse_args() method
args = argparser.parse_args()

INPUT_DIR = args.input_dir
OUTPUT_DIR = args.output_dir
DELIMITER = args.delimiter
DATE_PATTERN = args.date_pattern
DOCUMENT_ID_PATTERN = args.document_id_pattern
TIME_PATTERN = args.time_pattern
FILE_COUNT = args.file_count


if not os.path.isdir(INPUT_DIR):
    print("The path specified, {}, does not exist".format(INPUT_DIR))
    sys.exit()

if not os.path.isdir(OUTPUT_DIR):
    default_dir = "."
    print(
        "Output will be saved to {default_dir}, {output_dir} does not exist".format(
            default_dir=os.path.abspath(default_dir), output_dir=OUTPUT_DIR
        )
    )
    OUTPUT_DIR = default_dir


def process_rtf_to_dataframe(fpath, docid_patt, date_patt, time_patt):
    """
    Returns the document ID, date, time, and article text in a pandas DataFrame
    :param fpath: string, path to .RTF file
    :param docid_patt: string, regex pattern for document ID
    :param date_patt: string, regex pattern for date
    :param time_patt: string, regex pattern for time
    :return: pandas DataFrame
    """
    # read the raw content of the .RTF file
    with open(fpath) as f:
        rtf = f.read()
    # strip formatting to get plain text
    text = rtf_to_text(rtf).strip()
    # get document ID corresponding to each article
    doc_ids = re.findall(re.compile(docid_patt, re.M), text)
    # segmentation - split the text at each document ID, into individual articles
    articles = re.split("|".join(doc_ids), text)
    # the last item in the list after split operation should be blank (i.e. ''), so it can be dropped
    articles = articles[:-1]
    if len(articles) != len(doc_ids):
        print(
            'Text is not segmented appropriately, check regex "{docidpatt}": document ids {n_docid}, '
            "{n_articles}".format(
                n_docid=len(doc_ids), docidpatt=docid_patt, n_articles=len(articles)
            )
        )
        return
    # strip blank lines/spaces from the beginning/end of each article
    articles = [a.strip() for a in articles]
    # extract date from each article
    article_dates = list(map(lambda x: find_in_text(date_patt, x), articles))
    # extract time from each article
    article_times = list(map(lambda x: find_in_text(time_patt, x), articles))
    # assemble dataframe
    data = pd.DataFrame(
        zip(doc_ids, article_dates, article_times, articles),
        columns=["document_id", "date", "time", "text"],
    )
    return data


def find_in_text(patt, txt):
    """
    Takes a regular expression pattern and string input, returns the match found
    :param patt: string, regular expression
    :param txt: string, text to be searched
    :return: string, match found in text
    """
    patt_multiline = re.compile(patt, re.M)
    pattmatch = re.search(patt_multiline, txt)
    if pattmatch:
        res = pattmatch.group(0)
    else:
        res = None
    return res


def main():
    """
    Wrapper for processing .RTF files, iterates over all files ending in .rtf in the indicated directory
    :return:
    """
    data = []
    counter = 0
    for filepath in glob.iglob(os.path.join(INPUT_DIR, "*.rtf")):
        if counter >= FILE_COUNT:
            break
        data.append(
            process_rtf_to_dataframe(
                filepath,
                docid_patt=DOCUMENT_ID_PATTERN,
                date_patt=DATE_PATTERN,
                time_patt=TIME_PATTERN,
            )
        )
        counter += 1
    result = pd.concat(data)
    outpath = os.path.join(
        OUTPUT_DIR,
        "result_{timestamp}.txt".format(
            timestamp=datetime.now().strftime("%Y%m%d%H%m%S")
        ),
    )
    print("Saving file: {}".format(os.path.abspath(outpath)))
    result.to_csv(outpath, sep=DELIMITER, index=None)
    print("Done.")


if __name__ == "__main__":
    main()
