# 🏳️‍⚧️ Transdoc 🏳️‍⚧️

A simple tool for transforming Python docstrings by embedding results from
Python function calls.

## Installation

`pip install transdoc`

## Usage

Creating transformation rules is as simple as defining Python functions.

```py
# rules.py
def my_rule() -> str:
    '''
    A simple rule for rewriting docstrings
    '''
    return f"This text was added by Transdoc!"
```

They can then be used by placing their name within `{{` double braces `}}` in
any docstring.

```py
# program.py
def say_hi(name: str) -> str:
    '''
    Says hello to someone.
    {{my_rule}}
    '''
    return f"Hello, {name}!"
```

By executing `transdoc program.py -o program_transformed.py -r rules.py`,
Transdoc will produce a file `program_transformed.py` with the following
contents:

```py
# program.py
def say_hi(name: str) -> str:
    '''
    Says hello to someone.
    This text was added by Transdoc!
    '''
    return f"Hello, {name}!"
```

Rules can be as complex as you need, accepting any number of arguments. You can
call them like you would call the original Python function.

```py
# rules.py
def repeat(text: str, n: int = 2) -> str:
    '''
    Repeat the given text any number of times.
    '''
    return " ".join([text for _ in range(n)])
```

Using this rule to transform the following code

```py
def say_hi(name: str) -> str:
    '''
    Says hello to someone.
    {{repeat('wowee!')}}
    {{repeat('WOWEE!', n=5)}}
    '''
    return f"Hello, {name}!"
```

will produce this result:

```py
def say_hi(name: str) -> str:
    '''
    Says hello to someone.
    Wowee! Wowee!
    WOWEE! WOWEE! WOWEE! WOWEE! WOWEE!
    '''
    return f"Hello, {name}!"
```

Since passing a single string as an argument is so common, Transdoc adds a
special syntax for this. Simply place the string argument in square brackets.

```py
def mdn_link(e: str) -> str:
    '''
    Return a Markdown-formatted link for an HTML element
    '''
    return (
        f"[View <{e}> on MDN]"
        f"(https://developer.mozilla.org/en-US/docs/Web/HTML/Element/{e})"
    )
```

Using this rule to transform the following code

```py
def make_link(text: str, href: str) -> str:
    '''
    Generate an HTML link.
    {{mdn_link[a]}}
    '''
    # Please don't write code this insecure in real life
    return f"<a href={href}>{text}</a>"
```

will produce this result:

```py
def make_link(text: str, href: str) -> str:
    '''
    Generate an HTML link.
    [View <a> on MDN](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a)
    '''
    # Please don't write code this insecure in real life
    return f"<a href={href}>{text}</a>"
```

## Library usage

Transdoc also offers a simple library which can be used to perform these
operations programmatically.

```py
import transdoc

def fancy():
    return "✨fancy✨"

def my_function():
    '''Wow this is some {{fancy}} documentation'''


result = transdoc.transform(
    my_function,  # Code to transform
    [fancy],  # Rules to use in transformation (or a module containing rules)
)
# Result now contains a string with the transformed source code for my_function
```

## Integration with build systems

You can integrate Transdoc with project management systems and use it as a
pre-build script, so that your docstrings can be automatically built right
before packaging and distributing your project.

### Poetry

The system is undocumented and unstable, however it is possible (according to
[this GitHub comment](https://github.com/python-poetry/poetry/issues/5539#issuecomment-1126818974))
to get a pre-build script added.

In `pyproject.toml`:

```toml
[tool.poetry.build]
generate-setup-file = false
script = "build.py"

# ...

[build-system]
requires = ["poetry-core", "transdoc"]
build-backend = "poetry.core.masonry.api"
```

In a file `build.py`:

```py
import transdoc

exit(transdoc.main("src", "rules.py", "build_dir", force=True))
```
