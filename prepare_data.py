
import sys
sys.path.append('/home/jovyan/ru_transformers/gpt_env/lib/python3.6/site-packages')
import argparse
import os
import pickle
from tqdm import tqdm, trange
from multiprocessing import  Pool
from multiprocessing import cpu_count
import math
from tokenizer_gpt2 import GPT2VocabTokenizer

parser = argparse.ArgumentParser()
parser.add_argument("--jobs", type=int, default=-1,
                    help="count of workers")
parser.add_argument("--block_size", type=int, default=512,
                    help="block size")
parser.add_argument("--batch_size", type=int, default=10,
                    help="batch size")
parser.add_argument('--path_to_files', type=str, default='', help="For distant debugging.")
parser.add_argument('--path_to_vocab', type=str, default='', help="For distant debugging.")
parser.add_argument("--overwrite_cache", action='store_true',
                    help="overwrite cache")
parser.add_argument("--local_rank", type=int, default=-1,
                    help="block size")
args = parser.parse_args()

tokenizer = GPT2VocabTokenizer.from_pretrained(args.path_to_vocab)



def process_file(file_path):
    directory, filename = os.path.split(file_path)
    directory = os.path.join(directory, f'cached_{args.block_size}_{len(tokenizer.vocab)}')
    os.makedirs(directory, exist_ok=True)
    cached_features_file = os.path.join(directory, f'cached_lm_{args.block_size}_{len(tokenizer.vocab)}_{filename}')
    examples = []
    # add random shift

    if os.path.exists(cached_features_file) and not args.overwrite_cache:
        # logger.info("Loading features from cached file %s", cached_features_file)
        with open(cached_features_file, "rb") as handle:
            examples = pickle.load(handle)
    else:
        # logger.info("Creating features from dataset file at %s", directory)

        examples = []
        with open(file_path, encoding="utf-8") as f:
            text = f.read()

        tokenized_text = tokenizer.encode(text)

        for i in range(0, len(tokenized_text) - args.block_size + 1, args.block_size):  # Truncate in block of block_size
            examples.append(tokenizer.build_inputs_with_special_tokens(tokenized_text[i: i + args.block_size]))
        # Note that we are loosing the last truncated example here for the sake of simplicity (no padding)
        # If your dataset is small, first you should loook for a bigger one :-) and second you
        # can change this behavior by adding (model specific) padding.

        # logger.info("Saving features into cached file %s", cached_features_file)
        with open(cached_features_file, "wb") as handle:
            pickle.dump(examples, handle, protocol=pickle.HIGHEST_PROTOCOL)


def prepare(files):
    for file in files:
        process_file(file)

if __name__ == "__main__":
    workers = args.jobs if args.jobs > 0 else cpu_count()
    files = list(filter(lambda x: x[-4:] == '.txt', os.listdir(args.path_to_files)))
    files=[args.path_to_files+'/'+file for file in files]
    count_task = len(files) // (args.batch_size * workers)
    batch_size = args.batch_size
    pool = Pool(workers)
    for ind in tqdm(range(0, len(files) + 1, batch_size * workers)):
        end_ind = ind + batch_size * workers
        if end_ind > len(files) + 1:
            end_ind = len(files) + 1
        pool.map(prepare,[files[i:i+batch_size] for i in range(ind,end_ind,batch_size)])
        #prepare(files[ind:end_ind])