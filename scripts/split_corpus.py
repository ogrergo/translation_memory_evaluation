if __name__ =='__main__':
    import sys

    if len(sys.argv) != 4:
        print("Usage: python %s file_in file_fr_out file_en_out"%sys.argv[0], file=sys.stderr)
        sys.exit(1)

    file_in = sys.argv[1]
    file_fr_out = sys.argv[2]
    file_en_out = sys.argv[3]

    with open(file_in) as fp:
        with open(file_fr_out, 'w') as fp_fr, open(file_en_out, 'w') as fp_en:
            for l in fp:
                l = l.strip()
                if not l:
                    continue
                fr, en = l.split('\t')
                fp_en.write("{}\n".format(en))
                fp_fr.write("{}\n".format(fr))
