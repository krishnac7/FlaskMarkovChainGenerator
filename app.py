import os
from flask import Flask
from collections import defaultdict, Counter
from numpy import cumsum, sum, searchsorted
from numpy.random import rand
from random import randint
app = Flask(__name__)


class MarkovChain(object):
    # Initiate our MarkovChain
    def __init__(self, order=1):

        # Create our transitions
        self._transitions = defaultdict(int)

        # Set our order
        self._order = order

        # Create an empty list of letters
        self._symbols = list()
         # Train our chain on words
    def train(self, sequence):
        # Turn our words in to a list of characters
        sequence_list = list(set(sequence))

        # Add our sequence passed in to our chain
        self._symbols.extend(sequence_list)

        # For each character in our chain
        for i in range(len(sequence)-self._order):
            # "Letters i to i + 2 will be once more likely to be followed by i + 3"
            self._transitions[sequence[i:i+self._order], sequence[i+self._order]] += 1
    # Takes in input a string and predicts the next character.
    def predict(self, symbol):
        # We expect a certain amount of letters to get started
        if len(symbol) != self._order:
            raise ValueError('Expected string of %d chars, got %d' % (self._order, len(symbol)))

        # Grab the probably letters that come after the symbol passed in
        probs = [self._transitions[(symbol, s)] for s in self._symbols]

        # Add some weighted randomness to the result
        return self._symbols[self._weighted_pick(probs)]
     # Generates n characters from start.
    def generate(self, start, n):
        result = start

        # Foreach in n
        for i in range(n):
            # Get the next letter
            new = self.predict(start)

            # Add that letter to our output
            result += new

            # Our next start should be the new, minus the first letter of the old. So "abc" -> "abcd" -> "bcd"
            start = start[1:] + new
        return result

    # Weighted random selection returns n_picks random indexes. The chance to pick the index i is given by weights[i].
    @staticmethod
    def _weighted_pick(weights):
        return searchsorted(cumsum(weights), rand()*sum(weights))

order = 15

in_text = ''

resp = open('2states.txt')
in_text += resp.read()

mc = MarkovChain(order=order)
mc.train(in_text)

# Get a random part of the text to start reading from
pos = randint(0, len(in_text) - order + 1)

# Get some text to start with
start = in_text[pos:pos+order]

print(mc.generate(start, 1000))

@app.route("/")
def hello():
    # Get a random part of the text to start reading from
    pos = randint(0, len(in_text) - order + 1)

    # Get some text to start with
    start = in_text[pos:pos+order]

    return """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Markov chain by Krishna</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container">
  <blockquote class="blockquote">
    <p>{story}</p>
    <footer>Based on 2states</footer>
  </blockquote>
  <input class ='.btn-primary' type="button" value="New Narrative" onClick="window.location.reload()">
</div>
</body>
    """.format(story=mc.generate(start, 500))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
