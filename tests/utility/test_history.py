import datetime
from headless.utility.history import History


def test_history():
    h = History(capacity=4)
    h.add("one")
    assert "one" in h
    assert "one" == list(h[datetime.datetime.now()])[0].item

    h.add("two")
    assert "two" in h
    assert "two" == list(h[datetime.datetime.now()])[1].item

    h.add("three")
    assert "three" in h
    assert "three" == list(h[datetime.datetime.now()])[2].item

    h.add("four")
    h.add("five")
    assert "two" == list(h[datetime.datetime.now()])[0].item
