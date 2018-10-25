from tqdm import tqdm

from sentence import Sentence


def init_dataset(src_path, tgt_path, src_out, tgt_out):
    with open(src_path) as fp_in_src, open(tgt_path) as fp_in_tgt:
        with open(src_out, 'w') as fp_out_src, open(tgt_out, 'w') as fp_out_tgt:
            for src_l, tgt_l in tqdm(zip(fp_in_src, fp_in_tgt)):
                src, tgt = Sentence.deserialize(src_l), Sentence.deserialize(tgt_l)
                fp_out_src.write("{}|{}\n".format(src.source, tgt.key))
                fp_out_tgt.write("{}\n".format(tgt.source))


