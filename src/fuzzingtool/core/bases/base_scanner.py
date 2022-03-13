# Copyright (c) 2020 - present Vitor Oriel <https://github.com/VitorOriel>
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

from abc import ABC, abstractmethod
from queue import Queue

from ...objects import Result, ScannerResult


class BaseScanner(ABC):
    """Base scanner"""
    def __init__(self):
        self.payload_queue = Queue()

    def __str__(self) -> str:
        return type(self).__name__

    @abstractmethod
    def inspect_result(self, result: Result) -> None:
        """Inspects the FuzingTool result to add new information if needed

        @type result: Result
        @param result: The result object
        """
        scanner_name = str(self)
        result.scanners_res[scanner_name] = ScannerResult(scanner_name)

    @abstractmethod
    def scan(self, result: Result) -> bool:
        """Scan the FuzzingTool result

        @type result: Result
        @param result: The result object
        @reeturns bool: A match flag
        """
        pass

    @abstractmethod
    def process(self, result: Result) -> None:
        """Process the FuzzingTool result

        @type result: Result
        @param result: The result object
        """
        pass

    def _enqueue_payload(self, result: Result, payload: str) -> None:
        self.payload_queue.put(payload)
        scanner_res: ScannerResult = self._get_self_res(result)
        scanner_res.queued_payloads += 1

    def _get_self_res(self, result: Result) -> ScannerResult:
        return result.scanners_res[str(self)]
