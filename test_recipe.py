import pytest
from pathlib import Path


from recipe import body_only, html_to_text, load_my_custom_stream


def test_body_only():
    html = Path('notebooks/b.html').read_text(encoding='utf-8')
    body = body_only(html)
    # print(body)


def test_html_to_text():
    html = Path('notebooks/b.html').read_text(encoding='utf-8')
    # TODO type?
    body = body_only(html)
    # print(html_to_text(body.get_text()))
    print(html_to_text(body.get_text()))


# @pytest.mark.skip(reason="XXX")
def test_load_my_custom_stream():
    all = list(load_my_custom_stream('notebooks/b.jsonl'))
    assert len(all) == 1
