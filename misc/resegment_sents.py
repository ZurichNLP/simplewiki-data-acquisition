import argparse
import csv
from typing import IO

from mosestokenizer import MosesSentenceSplitter

# intended to run on simplede_all.tsv as input, change column definitions if necessary


def parse_args():  # python3 resegment_sents.py --input-tsv simplede_all.tsv --output-tsv simplede_all.resegmented.tsv --language de
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-tsv",
        type=argparse.FileType("r"),
        metavar="PATH",
        help="input tsv with old segmentation",
    )
    parser.add_argument(
        "--output-tsv",
        type=argparse.FileType("w"),
        metavar="PATH",
        help="output tsv with new segmentation",
    )
    parser.add_argument(
        "-l",
        "--language",
        type=str,
        metavar="LANG",
        default="de",
        help="language for the moses sentence splitter to use",
    )
    args = parser.parse_args()
    return args


def create_new_segmentation(infile: IO, outfile: IO, lang: str):
    simple_fieldnames = [
        "simple_article_id",
        "simple_section_id",
        "simple_sent_id",
        "simple_url",
        "simple_article_title",
        "simple_section_title",
        "simple_sent",
        "de_article_title",
        "de_url",
        "simplede_sent",
    ]
    simple_reader = csv.DictReader(infile, simple_fieldnames, delimiter="\t")
    simple_writer = csv.DictWriter(
        outfile, simple_fieldnames, delimiter="\t", extrasaction="ignore"
    )

    last_article_id = None
    last_section_id = None
    last_line = None
    section_content = ""
    with MosesSentenceSplitter(lang) as splitsents:
        for line in simple_reader:
            # new section begins at article borders or within articles at section borders
            # in subsequent short articles, section ID does not necessarily change
            if (
                last_article_id != line["simple_article_id"]
                or last_section_id != line["simple_section_id"]
            ) and last_section_id is not None:
                sent_id = 1
                if section_content.strip():
                    for sent in splitsents([section_content]):
                        out_line = last_line
                        out_line.update(
                            {
                                "simple_sent": "NOT_PARALLEL",
                                "simplede_sent": sent,
                                "simple_sent_id": sent_id,
                            }
                        )
                        simple_writer.writerow(out_line)
                        sent_id += 1
                section_content = ""

            section_content += " " + line["simplede_sent"].strip()
            last_article_id = line["simple_article_id"]
            last_section_id = line["simple_section_id"]
            last_line = line

        for sent in splitsents([section_content]):
            out_line = last_line
            out_line.update(
                {"simple_sent": "NOT_PARALLEL", "simplede_sent": sent, "simple_sent_id": sent_id}
            )
            simple_writer.writerow(out_line)
            sent_id += 1


def main(args: argparse.Namespace):
    create_new_segmentation(args.input_tsv, args.output_tsv, args.language)


if __name__ == "__main__":
    args = parse_args()
    main(args)
