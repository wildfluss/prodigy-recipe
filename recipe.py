# https://prodi.gy/docs/custom-recipes

import prodigy

from typing import Generator, TypedDict, Optional
import srsly
import bs4
from bs4 import BeautifulSoup, Tag
import en_core_web_sm

nlp = en_core_web_sm.load()


# from notebooks/prodigy.ipynb


def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, features="html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()
    return text


def body_only(html: str) -> Tag | bs4.element.NavigableString | None:
    soup = BeautifulSoup(html, features="html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    body = soup.find('body')
    return body


# https://docs.python.org/3/library/typing.html#typing.TypedDict
class Example(TypedDict):
    html: str
    text: str


def g(data: Example) -> Optional[Example]:
    body = body_only(data['html'])
    if body is not None:
        # Keep only body because page HTML breaks prodigy CSS
        example: Example = {"html": str(body),  # XXX 123 does not typecheck though https://stackoverflow.com/q/76373303/7424605
                            "text": html_to_text(body.get_text())}
        return example
    return None


def text_to_tokens(text):
    doc = nlp(text)
    # https://prodi.gy/docs/api-interfaces#relations-settings
    id = 0
    tokens = []
    for tok in doc:
        # {"text": "My", "start": 0, "end": 2, "id": 0, "ws": true},
        t = {"text": tok.text, "start": tok.idx, "end": tok.idx +
             len(tok.text), "id": id, "ws": tok.is_space}
        # print(t)
        tokens.append(t)
        id = id + 1
        # break
    return tokens


def load_my_custom_stream(source: str = "b.jsonl") -> Generator:
    for data in srsly.read_jsonl(source):
        b = g(data)
        if b is not None:
            tokens = text_to_tokens(b['text'])
            yield {"html": b['html'], "text": b['text'], "tokens": tokens}


blocks = [
    {"view_id": "relations"}
]


@prodigy.recipe(
    "my-custom-recipe",
    dataset=("Dataset to save answers to", "positional", None, str),
    view_id=("Annotation interface", "option", "v", str),
    source=("Source JSONL file", "option", "s", str)
)
def my_custom_recipe(dataset, view_id="html", source="./notebooks/b.jsonl"):  # TODO remove view_id
    # Load your own streams from anywhere you want
    stream = load_my_custom_stream(source)

    def update(examples):
        # This function is triggered when Prodigy receives annotations
        print(f"Received {len(examples)} annotations!")

    # https://support.prodi.gy/t/enabling-both-assign-relations-and-select-spans-in-custom-relations-recipe/3647/5?u=ysz
    return {
        "view_id": "blocks",
        "dataset": dataset,  # Name of dataset to save annotations
        "stream": stream,  # Incoming stream of examples
        "config": {"blocks": blocks,
                   "labels": ["Within the", "Near the"],
                   "relations_span_labels": ["PATHOLOGY", "DESCRIPTOR", "LOCATION"]}
    }
