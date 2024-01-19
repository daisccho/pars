from natasha import (
    Segmenter,
    MorphVocab,
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    NamesExtractor,
    Doc
)
from config import list_pers, list_land

def parse_text(text):
    pers_dict = []
    land_dict = []

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    doc.tag_ner(ner_tagger)
    for span in doc.spans:
       span.normalize(morph_vocab)

    for chart in doc.spans:
        if (chart.type == 'PER') & (chart.normal not in pers_dict) & (chart.normal in list_pers):
            pers_dict.append(chart.normal)
        if (chart.type == 'LOC') & (chart.normal not in land_dict) & (chart.normal in list_land):
            land_dict.append(chart.normal)

    return pers_dict, land_dict
