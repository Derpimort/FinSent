"""
 Created on Sun Sep 06 2020 21:59:25

 @author: Derpimort
"""

import os
import random
import string
import numpy as np
import pandas as pd
from pytorch_pretrained_bert.modeling import BertForSequenceClassification
from pytorch_pretrained_bert.tokenization import BertTokenizer
from nltk.tokenize import sent_tokenize
# chunks, InputExample, convert_examples_to_feature
from finbert.utils import *

from .constants import DATA_DIR, MODEL_DIR

BATCH_SIZE = 5


def get_sentiment(text, model, tokenizer=None, write_to_csv=False, path=None):
    """
    Predict sentiments of sentences in a given text. The function first tokenizes sentences, make predictions and write
    results.

    Parameters
    ----------
    text: string
        text to be analyzed
    model: BertForSequenceClassification
        path to the classifier model
    write_to_csv (optional): bool
    path (optional): string
        path to write the string

    Returns
    --------
    results:    pd.DataFrame
                result df with columns [sentence, logit, prediction, sentiment_score]
    """
    # print(text)
    model.eval()

    tokenizer = BertTokenizer.from_pretrained(
        'bert-base-uncased') if tokenizer is None else tokenizer

    sentences = sent_tokenize(text) if isinstance(text, str) else text

    label_list = ['positive', 'negative', 'neutral']
    label_dict = {0: 'positive', 1: 'negative', 2: 'neutral'}
    result = pd.DataFrame(
        columns=['sentence', 'logit', 'prediction', 'sentiment_score'])
    for batch in chunks(sentences, BATCH_SIZE):

        examples = [InputExample(str(i), sentence)
                    for i, sentence in enumerate(batch)]

        features = convert_examples_to_features(
            examples, label_list, 64, tokenizer, verbose=False)

        all_input_ids = torch.tensor(
            [f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor(
            [f.input_mask for f in features], dtype=torch.long)
        all_segment_ids = torch.tensor(
            [f.segment_ids for f in features], dtype=torch.long)

        with torch.no_grad():
            logits = model(all_input_ids, all_segment_ids, all_input_mask)
            logits = softmax(np.array(logits))
            sentiment_score = pd.Series(logits[:, 0] - logits[:, 1])
            predictions = np.squeeze(np.argmax(logits, axis=1))

            batch_result = {'sentence': batch,
                            'logit': list(logits),
                            'prediction': predictions,
                            'sentiment_score': sentiment_score}

            batch_result = pd.DataFrame(batch_result)
            result = pd.concat([result, batch_result], ignore_index=True)

    result['prediction'] = result.prediction.apply(lambda x: label_dict[x])
    if write_to_csv:
        result.to_csv(path, sep=',', index=False)

    return result


if __name__ == "__main__":
    text = "On Friday, ITC Ltd said it is considering a merger of its three wholly-owned subsidiaries- Sunrise Foods, Hobbits International Foods and Sunrise Sheetgrah - with itself. A board meeting will be held on the same on 4 September 2020, the company"
    model = BertForSequenceClassification.from_pretrained(
        MODEL_DIR, num_labels=3, cache_dir=None)
    random_filename = ''.join(random.choice(
        string.ascii_letters) for i in range(10))
    output = random_filename + '.csv'
    get_sentiment(text, model, write_to_csv=True,
                  path=os.path.join(DATA_DIR, output))
