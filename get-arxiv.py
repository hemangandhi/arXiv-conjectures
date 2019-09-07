import requests as req
import atoma
import nltk

ARXIV_BASE_URL = "http://export.arxiv.org/api/query"

def query_arxiv(query):
    response = req.get(ARXIV_BASE_URL, params={'search_query': query})
    feed = atoma.parse_atom_bytes(response.content)
    return feed

def remove_latex(text):
    no_tex = ''
    in_math_mode = False
    backslash = False
    for i in text:
        if i == '$' and not backslash:
            in_math_mode = not in_math_mode
        backslash = not backslash and i == '\\'
        if not in_math_mode and i != '$':
            no_tex += i
    return no_tex

def split_at(it, elem):
    acc = []
    for i in it:
        acc.append(i)
        if i == elem:
            yield acc
            acc = []
    yield acc

def guess_conjecture_name(tokens):
    # TODO: this might actually have to be a parser for some
    # sort of grammar
    def is_ok_tag(token, tag):
        STOP_WORDS = ['implies', 'imply', 'proves', 'proven', 'prove', 'that', 'the', 'a', 'our']
        if token in STOP_WORDS:
            return False
        # Assumption: the only time tag == token is for punctuation
        return tag != token

    if tokens[-1][0] != 'conjecture':
        return None

    idx = len(tokens) - 1
    while idx >= 0 and is_ok_tag(*tokens[idx]):
        idx -= 1
    name = " ".join(i[0] for i in tokens[idx + 1:])
    if name == 'conjecture':
        return None
    return name

def conjecture_names_from_feed(feed):
    # This is so that we get a list of conjectures per article
    def summarize(summary):
        summary_words = nltk.word_tokenize(summary)
        summary_tagged = nltk.pos_tag(summary_words)
        for split in split_at(summary_tagged, ('conjecture', 'NN')):
            name = guess_conjecture_name(split)
            if name is not None:
                yield name

    for article in feed.entries:
        yield article.title.value, set(summarize(remove_latex(article.summary.value)))

c = conjecture_names_from_feed(query_arxiv('all:conjecture'))
for title, conjs in c:
    print(title)
    for conj in conjs:
        print('Conjecture: ', conj)
