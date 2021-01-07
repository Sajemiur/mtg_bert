import torch
import pandas as pd
import os
from tqdm import tqdm
import sys
import numpy as np
from transformers import BertTokenizer, BertForSequenceClassification
import mtg.mtg_processor as mtgpre
from asgiref.sync import sync_to_async

from torch.utils.data import TensorDataset, DataLoader, SequentialSampler

import logging

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

model_state_dict = None

args = {
    "no_cuda": False,
    "max_seq_length": 512,
    "do_lower_case": True,
    "train_batch_size": 32,
    "eval_batch_size": 32,
    "learning_rate": 3e-5,
    "num_train_epochs": 4.0,
    "warmup_proportion": 0.1,
    "no_cuda": False,
    "local_rank": -1,
    "seed": 42,
    "gradient_accumulation_steps": 16,
    "optimize_on_cpu": False,
    "fp16": False,
    "loss_scale": 128,
    "additional_special_tokens": ['[TYP]', '[UTYP]', '[CMC]', '[PWR]', '[MANA]', '[TGH]',
                                  '[NAME]', '[TXT]', '[CLR]', '[SIDE]', '[STYP]'],
    "head_mask": torch.tensor([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1], dtype=torch.float)
}


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, labels=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For single
            sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second sequence.
            Only must be specified for sequence pair tasks.
            labels: (Optional) [string]. The label of the example. This should be
            specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.labels = labels


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_ids):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_ids = label_ids


def card_concat(card):
    string = ' [NAME] ' + card['name']
    string += (' [CLR] ' + "".join(card['colors']) if len(card['colors']) > 0 else "")
    string += ' [CMC] ' + str(int(card['convertedManaCost']))
    string += (' [MANA] ' + card['manaCost'] if 'manaCost' in card else "")
    string += (' [UTYP] ' + " ".join(card['subtypes']) if len(card['subtypes']) > 0 else "")
    string += (' [STYP] ' + " ".join(card['supertypes']) if len(card['supertypes']) > 0 else "")
    string += (' [TYP] ' + " ".join(card['types']) if len(card['types']) > 0 else "")
    string += (' [PWR] ' + card['power'] if 'power' in card else "")
    string += (' [TGH] ' + card['toughness'] if 'toughness' in card else "")
    string += (' [LOY] ' + card['loyalty'] if 'loyalty' in card else "")
    string += (' [TXT] ' + card['text'] if 'text' in card else "")
    return string


def get_test_examples(df):
    """Creates examples for the training and dev sets."""
    examples = []
    for (i, row) in enumerate(df.values):
        guid = i
        text_a = row[0]
        text_b = row[1]

        examples.append(
            InputExample(guid=guid, text_a=text_a, text_b=text_b, labels=[]))
    return examples


def convert_examples_to_features(examples, label_list, tokenizer, max_seq_length=512, labels=True):
    """Loads a data file into a list of `InputBatch`s."""

    label_map = {label: i for i, label in enumerate(label_list)}

    features = []
    for (ex_index, example) in enumerate(examples):
        tokens_a = tokenizer.tokenize(example.text_a)

        tokens_b = None
        if example.text_b:
            tokens_b = tokenizer.tokenize(example.text_b)
            # Modifies `tokens_a` and `tokens_b` in place so that the total
            # length is less than the specified length.
            # Account for [CLS], [SEP], [SEP] with "- 3"
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            # Account for [CLS] and [SEP] with "- 2"
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[:(max_seq_length - 2)]

        tokens = ["[CLS]"] + tokens_a + ["[SEP]"]
        segment_ids = [0] * len(tokens)

        if tokens_b:
            tokens += tokens_b + ["[SEP]"]
            segment_ids += [1] * (len(tokens_b) + 1)

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real
        # tokens are attended to.
        input_mask = [1] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding = [0] * (max_seq_length - len(input_ids))
        input_ids += padding
        input_mask += padding
        segment_ids += padding

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        if labels is True:
            label_id = float(label_map[example.labels])
        else:
            label_id = 2.0

        if ex_index < 0:
            logger.info("*** Example ***")
            logger.info("guid: %s" % (example.guid))
            logger.info("tokens: %s" % " ".join(
                [str(x) for x in tokens]))
            logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
            logger.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
            logger.info(
                "segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
            logger.info("label: %s (id = %s)" % (example.labels, label_id))

        features.append(
            InputFeatures(input_ids=input_ids,
                          input_mask=input_mask,
                          segment_ids=segment_ids,
                          label_ids=label_id))
    return features


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()


class Model:

    def __init__(self):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased",
                                                       do_lower_case=True,
                                                       additional_special_tokens=['[TYP]', '[UTYP]', '[CMC]', '[PWR]',
                                                                                  '[MANA]', '[TGH]', '[NAME]', '[TXT]',
                                                                                  '[CLR]', '[SIDE]', '[STYP]'])
        self.label_list = ["neutral", "entailment"]
        self.batch_size = 32

        self.model = BertForSequenceClassification.from_pretrained("mtg/model/",
                                                                   num_labels=2, local_files_only=True)
        self.model.resize_token_embeddings(len(self.tokenizer))
        self.model.to(self.device)

    async def predict(self, card):
        cards_names, cards_imgs, df = await sync_to_async(mtgpre.prepare_prediction_data, thread_sensitive=True)(card)
        test_examples = get_test_examples(df)

        test_features = convert_examples_to_features(
            test_examples, self.label_list, self.tokenizer, labels=False)

        all_input_ids = torch.tensor([f.input_ids for f in test_features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in test_features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in test_features], dtype=torch.long)

        test_data = TensorDataset(all_input_ids, all_input_mask, all_segment_ids)

        # Run prediction for full data
        test_sampler = SequentialSampler(test_data)
        test_dataloader = DataLoader(test_data, sampler=test_sampler, batch_size=self.batch_size)

        all_logits = None

        for step, batch in enumerate(tqdm(test_dataloader, desc="Prediction Iteration")):
            input_ids, input_mask, segment_ids = batch
            input_ids = input_ids.to(self.device)
            input_mask = input_mask.to(self.device)
            segment_ids = segment_ids.to(self.device)

            with torch.no_grad():
                logits = self.model(input_ids, segment_ids, input_mask)[0]
                logits = logits.sigmoid()

            yield {cards_names[step * self.batch_size + i]:
                       (cards_imgs[step * self.batch_size + i], format(elem[1] * 100, '.2f'))
                   for i, elem in enumerate(logits.detach().cpu().numpy())}

            if all_logits is None:
                all_logits = logits.detach().cpu().numpy()
            else:
                all_logits = np.concatenate((all_logits, logits.detach().cpu().numpy()), axis=0)

        pd.merge(pd.DataFrame(cards_names), pd.DataFrame(all_logits, columns=self.label_list)['entailment'])
        pd.DataFrame(all_logits, columns=self.label_list).to_csv('last_search.csv', index=None)
