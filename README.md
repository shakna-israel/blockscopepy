# blockscope

Experimental block-scoping for Python.

---

# Reasoning

Ever get sick of temporary variables in Python? I do.

In something like Lua I can throw them into a do-block and they will shadow correctly, and be tossed when I'm done, with a clear creation/removal point.

In Python, I need to remember to clean them up if they're large, or go to the effort of writing a context manager for every little thing.

Which is annoying, and feels unnecessary.

At the expense of adding a `dict` to every single `object`, and possibly breaking random shit, we can monkey-patch `object` so that it is automatically a context manager:

```
import blockscope

with {"a": 12} as obj:
	print(obj)
```

Which, of course, lets us do actual practical blockscoping stuff like:

```
import subprocess
import json

import blockscope

with subprocess.run(["tree", "-ixpsugJ", "."], capture_output=True) as data:
	tree = json.loads(data.stdout.decode())

print(tree)
```

---

# Implementation & Safety

## Safety

***Holy shit. Run!***

Most, if not all, of the internals of `blockscope` go outside the CPython API. They rely on classes that may or may not exist on your version of Python.

It's also ***C***Python's API. There's practically no way this runs on PyPy or any of the Java implementations, or MicroPython or any of that.

As we attach a `dict` to `object`, we also open the door for other code to modify `object`, which would usually be a `TypeError`, and some code may _rely_ on that behaviour. Causing subtle and unexpected bugs in all kinds of libraries - some of which may be in the Python standard library.

C-based libraries that expect `object` to be of a certain size may run into some _very_ subtle bugs as well. We've only really added a pointer, but that's enough to cause some true havoc. You might be able to avoid problems by importing `blockscope` _after_ any C-based library. Maybe. (There is also the strong possibility that the C-based library will _ignore_ this particular hack, but it can't be guaranteed).

Finally, pay special note to how we don't actually call any function from inside `blockscope`. Once you import it, you're done. It monkey-patches `object` the moment you pull it in.

## Performance

***You managed to make Python even slower, you asshole!***

There is a very good reason that the standard Python `object` doesn't have a `__dict__` attached to it. Both memory and performance reasons.

As we attach a `dict` to `object`, we add overhead. Which may not be insignificant. This overhead is both in the memory side of things, and the way Python looks up methods on objects when it tries to do things.

## Breakage

I've mentioned several times that this may subtly break things.

This is a best-guess.

Whilst all the built-in context managers (like `open`) I've tried seem to work absolutely fine with the change, I have no way of knowing that behaviour is consistent across all Python versions.

Libraries may also rely on modifying builtins raising a `TypeError`. (Such as checking if something _is_ a builtin). Therefore, we might be breaking random libraries in a very hard to debug way - making something permissable where it wasn't is much harder to find than an exception.

---

# Credit

Credit where credit is due, the fantastic [Armin Ronacher](https://lucumr.pocoo.org/) is the one who originally found a way to patch builtin methods.

Most of my work involved updating his work to be more compatible with some of the changes that CPython has gone through over time, and clearing up some of the error reporting.

---

# License

As of writing, this project is licensed under CC0.

See the `LICENSE` file for actual legally binding text.
