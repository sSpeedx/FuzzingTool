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

from requests import PreparedRequest, Response

from ..utils.http_utils import build_raw_response_header, UrlParse, get_parsed_url


class HttpHistory:
    def __init__(self, response: Response, rtt: float):
        self.url = response.url
        self.method = response.request.method
        self.rtt = float('%.6f' % (rtt))
        self.status = response.status_code
        self.body_size = len(response.content)
        self.__response = response

    @property
    def parsed_url(self) -> UrlParse:
        return get_parsed_url(self.url)

    @property
    def raw_headers(self) -> str:
        return build_raw_response_header(self.__response)

    @property
    def headers_length(self) -> int:
        return len(self.raw_headers)

    @property
    def response_time(self) -> float:
        return self.__response.elapsed.total_seconds()

    @property
    def request_time(self) -> float:
        return float('%.6f' % (self.rtt - self.response_time))

    @property
    def request(self) -> PreparedRequest:
        """The request getter

        @returns Request: The request object
        """
        return self.__response.request

    @property
    def response(self) -> Response:
        """The response getter

        @returns Response: The response of the request
        """
        return self.__response
