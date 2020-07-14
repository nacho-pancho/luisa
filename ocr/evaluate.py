import numpy as np
import pandas as pd
from textdistance import levenshtein


def evaluate(submission_path, reference_path):
    """
    Calculates Levenshtein distance between submission and reference.
    """
    data = pd.read_csv(reference_path, delimiter='\t', index_col=0, names=['reference'])
    data = data.join(pd.read_csv(submission_path, delimiter='\t', index_col=0, names=['submission']))
    data.fillna('&', inplace=True)
    reference = data.reference.values
    submission = data.submission.values

    levenshtein_distance = np.vectorize(levenshtein.distance)
    results = levenshtein_distance(reference, submission) / data.reference.str.len().values
    return results.mean()
