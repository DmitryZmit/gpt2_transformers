from run_generation import sample_sequence
import json
import re
import torch

import numpy as np

from os.path import join
from transformers import GPT2LMHeadModel, GPT2Config
from tokenizer_gpt2 import GPT2VocabTokenizer

speaker1_token='[speaker1]'
speaker2_token='[speaker2]'

class Gen_answer():
    def __init__(self,args):
        print('Load models')

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.n_gpu = torch.cuda.device_count()
        args.device, args.n_gpu = self.device, self.n_gpu
        #########################################################################
        # Prepare Data Set
        ##########################################################################
        # enc = GPT2Tokenizer.from_pretrained(args.model_name_or_path)
        self.tokenizer = GPT2VocabTokenizer.from_pretrained(args.model_name_or_path + '/vocab.txt')
        self.tokenizer.add_tokens([speaker1_token,speaker2_token])
        self.config = GPT2Config.from_json_file(
            join(args.model_name_or_path, 'config.json'))

        #########################################################################
        # Prepare Model and Optimizer
        ##########################################################################
        self.model = GPT2LMHeadModel.from_pretrained(args.model_name_or_path )
        total_params = sum([np.prod(p.size()) for p in self.model.parameters()])
        print('Number of parameter = {}'.format(total_params))
        self.model.eval()

    def get_answer(self, context,t=1,tk=5,max_len=64):
        context_str=''
        count=1
        for rep in context:
            if count % 2 == 1:
                context_str += ' ' + speaker1_token + ' ' + rep
            else:
                context_str += ' ' + speaker2_token + ' ' + rep
        context_str+=' '+speaker2_token
        context_tokens = self.tokenizer.encode(context_str)
        out = sample_sequence(
            model=self.model,
            context=context_tokens,
            num_samples=1,
            length=max_len,
            temperature=t,
            top_k=tk,
            # top_p=0.3,
            device=self.device,

        )

        out = out[0, len(context_tokens):].tolist()

        res_text = self.enc.decode(out)
        res_text.replace(context_str,' ')
        answer_full=re.findall(r'', res_text)
        if len(answer_full)>0:
            answer = re.findall(r'[^\n]+', res_text)[0]
        else:
            answer=':)'
        return answer
