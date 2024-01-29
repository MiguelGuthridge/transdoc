# Transdoc 💗🤍💙

A simple tool for transforming Python docstrings, by embedding results from
Python function calls.

## Usage

Creating rules is as simple as defining Python functions.

They can then be used by placing their name within `{{` double braces `}}` in
any docstring.

```py
>>> import transdoc
>>> def my_rule() -> str:
...     """
...     A simple rule for rewriting docstrings
...     """
...     return f"This text was added by Transdoc!"
...
>>> def say_hi(name: str) -> str:
...     """
...     Says hello to someone.
...     {{my_rule}}
...     """
...     return f"Hello, {name}!"
...
>>> transdoc.transform(say_hi, [my_rule])
def say_hi(name: str) -> str:
    """
    Says hello to someone.
    This text was added by Transdoc!
    """
    return f"Hello, {name}!"

```

Rules can be as complex as you need, accepting any number of arguments. You can
call them like you would call the original Python function.

```py
>>> def repeat(text: str, n: int = 2) -> str:
...     """
...     Repeat the given text any number of times.
...     """
...     return " ".join([text for _ in range(n)])
...
>>> def say_hi(name: str) -> str:
...     """
...     Says hello to someone.
...     {{repeat('wowee!')}}
...     {{repeat('WOWEE!', n=5)}}
...     """
...     return f"Hello, {name}!"
...
>>> transdoc.transform(say_hi, [repeat])
def say_hi(name: str) -> str:
    """
    Says hello to someone.
    Wowee! Wowee!
    WOWEE! WOWEE! WOWEE! WOWEE! WOWEE!
    """
    return f"Hello, {name}!"
```

Since passing a single string as an argument is so common, Transdoc adds a
special syntax for this. Simply place the string argument in square brackets.

```py
>>> def mdn_link(e: str) -> str:
...     """
...     Return a Markdown-formatted link for an HTML element
...     """
...     return (
...         f"[View <{e}> on MDN]"
...         f"(https://developer.mozilla.org/en-US/docs/Web/HTML/Element/{e})"
...     )
...
>>> def make_link(text: str, href: str) -> str:
...     """
...     Generate an HTML link.
...     {{mdn_link[a]}}
...     """
...     # Please don't write code this insecure in real life
...     return f"<a href={href}>{text}</a>"
...
>>> transdoc.transform(make_link, [repeat])
def generate_link(text: str, href: str) -> str:
    """
    Generate an HTML link.
    [View <a> on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a)
    """
    # Please don't write code this insecure in real life
    return f"<a href={href}>{text}</a>"
```

### Note on REPL usage

Transdoc doesn't work in a REPL, since Python doesn't store the source code for
functions defined in a REPL environment. The above examples are instead used
to demonstrate Transdoc's capabilities.
