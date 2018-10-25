from tensor2tensor.data_generators import problem
from tensor2tensor.data_generators import text_problems
from tensor2tensor.data_generators import translate
from tensor2tensor.utils import registry

from run_train_inv_op import OUT_SENTS, OUT_TEST


@registry.register_problem
class TranslatePostprocess(translate.TranslateProblem):

  @property
  def vocab_type(self):
      return text_problems.VocabType.CHARACTER


  def generate_samples(self, data_dir, tmp_dir, dataset_split):
    """Instance of token generator for the WMT en->de task, training set."""

    if dataset_split == problem.DatasetSplit.TRAIN:
        dataset_path = OUT_SENTS
    else:
        dataset_path = OUT_TEST

    return text_problems.text2text_txt_iterator(dataset_path + "en",
                                                dataset_path + "fr")
