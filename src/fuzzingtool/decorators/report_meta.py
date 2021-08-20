# Copyright (c) 2021 Vitor Oriel <https://github.com/VitorOriel>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ..reports.BaseReport import BaseReport

def report_meta(cls: BaseReport) -> BaseReport:
    """Decorator to check for BaseReport metadata
    
    @type cls: BaseReport
    @param cls: The class that call this decorator
    """
    metadata = ['__author__', '__version__', '__alias__']
    classAttr = vars(cls)
    for meta in metadata:
        if meta not in classAttr:
            raise Exception(f"Metadata {meta} not specified on report {cls.__name__}")
    if not cls.__author__:
        raise Exception(f"Author cannot be empty on report {cls.__name__}")
    if not cls.__version__:
        raise Exception(f"Version cannot be blank on report {cls.__name__}")
    if not cls.__alias__:
        raise Exception(f"Alias cannot be blank on report {cls.__name__}")
    return cls