from flask import Flask, request, redirect, session, render_template_string
from EmojiTranslation import Translators
import dataclasses
import os

# Paramererize the constructor arguments
emoji_file = "./emoji_joined.txt"               # Emoji keyword file from emoji2vec
sent2vec_model = "./torontobooks_unigrams.bin"  # sent2vec model
nothing_lemma_func = lambda x: x                # Lemmatization function that does nothing

# Instantiate the exhaustive and part of speech translation algorithms
exh = Translators.ExhaustiveChunkingTranslation(emoji_file, sent2vec_model, nothing_lemma_func)
pos = Translators.PartOfSpeechEmojiTranslator(emoji_file, sent2vec_model, nothing_lemma_func)

index = """
<html>
    <head>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
        <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
        <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
        <style type="text/css">
           body { background: #EEE !important; } /* Adding !important forces the browser to overwrite the default style applied by Bootstrap */
        </style>
    </head>
    <body>
        <div class="container mt-5">
            <div class="card">
                <div class="card-header">
                    <h4>
                        <a href="https://www.alexday.me/pdf/emoji.pdf">
                            CoNFET: An English Sentence To Emojis Translation Algorithm
                        </a>
                    </h4>
                </div>
                <div class="card-body">
                    <form action="/summarize" method="post" class="form-group">
                        <div class="form-row">
                          <label for="sentence">Sentence:</label><br>
                          <input type="text" class="form-control" id="sentence" name="sentence" value="{{ session["summ"]["sentence"] }}"><br>
                          <label for="type">Type:</label><br>
                          <select id="type" class="form-control" name="type">
                            <option value="pos">Part of Speech</option>
                            <option value="exh">Exhaustive</option>
                          </select>
                        </div> <br>
                      <input type="submit" value="Submit" class="btn">
                    </form>

                    <table class="table table-bordered">
                        <thead>
                        <tr>
                            <th colspan="{{ session["summ"]["table_rows"] }}"> Emoji Summarization Result </th>
                        <tr>
                            <th> Emojis </th>
                        {% for emoji in session["summ"]["emojis"] %}
                            <td>{{ emoji }}</td>
                        {% endfor %}
                        </tr>
                        <tr>
                            <th> Emoji N-Grams </th>
                        {% for emoji in session["summ"]["emojis_n_grams"] %}
                            <td>{{ emoji }}</td>
                        {% endfor %}
                        </tr>
                        <tr>
                            <th> Sentence N-Grams </th>
                        {% for emoji in session["summ"]["n_grams"] %}
                            <td>{{ emoji }}</td>
                        {% endfor %}
                        </tr>
                        <tr>
                            <th> Similarity Scores </th>
                        {% for emoji in session["summ"]["uncertainty_scores"] %}
                            <td>{{ emoji }}</td>
                        {% endfor %}
                        </tr>
                    </table>
                </div>
            </div>
        </div>
    </body>
</html>
"""
app = Flask(__name__, static_url_path="", static_folder="")
app.secret_key = os.urandom(12)

@app.route("/summarize", methods=["POST"])
def summarize():
    if request.form["type"] == "exh":
        summ = exh.summarize(str(request.form["sentence"]))
    else:
        summ = pos.summarize(str(request.form["sentence"]))

    session["summ"] = dataclasses.asdict(summ)

    # Round numbers so they are human readable
    session["summ"]["elapsed_time"] = round(session["summ"]["elapsed_time"], 3)
    session["summ"]["uncertainty_scores"] = [round(1 - x, 3) for x in session["summ"]["uncertainty_scores"]]
    session["summ"]["emojis"] = list(session["summ"]["emojis"])
    session["summ"]["table_rows"] = len(session["summ"]["emojis"]) + 1
    session["summ"]["sentence"] = " ".join(session["summ"]["n_grams"])
    return redirect("/")

@app.route('/')
def root():
    if "summ" not in session:
        session["summ"] = { "emojis": "", "table_rows": 1, "sentence": "the dog ran fast"}
    print(session)
    return render_template_string(index)
# @app.route("/")
# def root():
