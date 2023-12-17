import tensorflow as tf
from transformers import TFBertForSequenceClassification, BertTokenizer
from transformers import BertTokenizer

bert_load_model = TFBertForSequenceClassification.from_pretrained(
    'indobenchmark/indobert-base-p2', num_labels=2)
bert_load_model.load_weights('temanTB-model.h5')
bert_tokenizer = BertTokenizer.from_pretrained('indobenchmark/indobert-base-p2')


def predict(text):
  # Sample text
  input_text = text 

  # Encode input text
  input_text_tokenized = bert_tokenizer.encode(input_text,
                                              truncation=True,
                                             padding='max_length',
                                             return_tensors='tf')

  # Make predictions
  bert_predict = bert_load_model(input_text_tokenized)
  # Softmax function to get classification results
  bert_output = tf.nn.softmax(bert_predict[0], axis=-1)

  sentiment_labels = ['positif', 'negatif']
  label = tf.argmax(bert_output, axis=1)
  label = label.numpy()

  print(input_text, ':', sentiment_labels[label[0]])
  return sentiment_labels[label[0]]

# predict('saya sakit sesak napas dan nyeri dada')