from transformers import BertTokenizer
newlinetoken='[endoftext]'
class GPT2VocabTokenizer(BertTokenizer):
    def __init__(
            cls,
            vocab_file,
            do_lower_case=False,
            do_basic_tokenize=True,
            never_split=None,
            **kwargs
    ):

        super().__init__(vocab_file=vocab_file,
                         do_lower_case=do_lower_case,
                         do_basic_tokenize=do_basic_tokenize,
                         never_split=never_split,
                         **kwargs
                         )
        super().add_tokens([newlinetoken])
    def encode(
        cls,
        text,
        text_pair=None,
        add_special_tokens=False,
        max_length=None,
        stride=0,
        truncation_strategy="longest_first",
        pad_to_max_length=False,
        return_tensors=None,
        **kwargs
    ):

        # prepare text to code \n
        text = text.replace('\n', f' {newlinetoken} ')
        return super().encode(text,
                        text_pair=text_pair,
                        add_special_tokens=add_special_tokens,
                        max_length=max_length,
                        stride=stride,
                        truncation_strategy=truncation_strategy,
                        pad_to_max_length=pad_to_max_length,
                        return_tensors=return_tensors,
                        **kwargs
                        )
    def decode(cls, token_ids, skip_special_tokens=False, clean_up_tokenization_spaces=True):
        result=super().decode(token_ids=token_ids, skip_special_tokens=skip_special_tokens, clean_up_tokenization_spaces=clean_up_tokenization_spaces)
        #convert newlinetoken  token to \n
        result = result.replace(newlinetoken, '\n')
        return  result
    def build_inputs_with_special_tokens(cls,token_ids):
        return token_ids
if __name__ == "__main__":

    tokenizer=GPT2VocabTokenizer.from_pretrained('/media/dmitryz/SAMSUNG_T5/models/gpt2_small_v5_v100')
    text='Привет как дела? \n Что делаешь :?'
    print(text)
    print(tokenizer.encode(text))
    print(tokenizer.decode(tokenizer.encode(text)))
    print(tokenizer.max_len_single_sentence)
