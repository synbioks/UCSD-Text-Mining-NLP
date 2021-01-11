import csv
import os
from os.path import join, abspath, isdir

from tqdm import tqdm

def process_raw_output(row, threshold=0, label_name=("UpRegulator", "DownRegulator", "CPR-5", "CPR-6", "Substrate", "false")):
    relation = label_name[int(row[2])]
    confidence = float(row[3])
    if confidence < threshold:
        return None
    if relation == "false":
        return None
    return {
        "id1": row[0],
        "id2": row[1],
        "relation": relation,
        "confidence": confidence
    }

def process_file(res_path, ann_path):

    ann = []
    with open(ann_path, "r", encoding="utf8") as fin:
        for line in fin:
            # remove all the RE lines (to keep this operation idempotent)
            if not line.startswith("R") and len(line) > 0:
                ann.append(line)
    
    raw = []
    with open(res_path, "r", encoding="utf8") as fin:
        for row in csv.reader(fin, delimiter="\t"):
            raw.append(row)
    raw = raw[1:]

    counter = 0
    for row in raw:
        re_obj = process_raw_output(row)
        if re_obj is not None:
            ann.append(f'R{counter}\t{re_obj["relation"]} Arg1:{re_obj["id1"]} Arg2:{re_obj["id2"]}\n')
            counter += 1
    
    with open(ann_path, "w", encoding="utf8") as fout:
        for line in ann:
            fout.write(line)

if __name__ == "__main__":

    dataset_dir = abspath("../datasets/acs")

    for pub_num in tqdm(os.listdir(dataset_dir)):
        # if pub_num != "sb5b00002":
        #     continue
        article_dir = join(dataset_dir, pub_num)
        assert(isdir(article_dir))
        process_file(
            res_path=join(article_dir, "re_output.tsv"), 
            ann_path=join(article_dir, f"{pub_num}.ann")
        )