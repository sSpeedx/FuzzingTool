## FuzzingTool
# 
# Authors:
#    Vitor Oriel C N Borges <https://github.com/VitorOriel>
# License: MIT (LICENSE.md)
#    Copyright (c) 2021 Vitor Oriel
#    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
## https://github.com/NESCAU-UFLA/FuzzingTool

from .Response import Response
from .RequestException import RequestException
from ..parsers.RequestParser import *
from ..IO.OutputHandler import outputHandler as oh
from ..IO.FileHandler import fileHandler as fh

import time
import socket
try:
    import requests
except:
    exit("Requests package not installed. Install all dependencies first.")

class Request:
    """Class that handle with the requests
    
    Attributes:
        url: The target URL
        method: The request method
        param: The parameter of the request
        httpHeader: The HTTP header
        proxy: The proxy used in the request
        proxyList: The list with valid proxies gived by a file
        timeout: The request timeout before raise a TimeoutException
        requestIndex: The request index
        parser: The request parser
        subdomainFuzzing: A flag to say if the fuzzing will occur on subdomain
    """
    def __init__(self, url: str, method: str, defaultParam: dict, httpHeader: dict):
        """Class constructor

        @type url: str
        @param url: The target URL
        @type method: str
        @param method: The request method
        @type defaultParam: dict
        @param defaultParam: The parameters of the request, with default values if are given
        @type httpHeader: dict
        @param httpHeader: The HTTP header of the request
        """
        self.__url = url
        self.__method = method
        self.__param = defaultParam
        self.__httpHeader = httpHeader
        self.__proxy = {}
        self.__proxyList = []
        self.__timeout = None
        self.__requestIndex = 0
        self.__setupHeader()
        self.__parser = RequestParser(self.__url, self.__httpHeader, self.__method, self.__param)
        self.__subdomainFuzzing = self.__parser.checkForSubdomainFuzz()
    
    def getUrl(self):
        """The url getter

        @returns str: The target URL
        """
        return self.__url

    def isUrlFuzzing(self):
        """The URL Fuzzing flag getter
        
        @returns bool: The URL Fuzzing flag
        """
        return self.__parser.isUrlFuzzing()

    def getProxy(self):
        """The proxy getter

        @returns dict: The proxy
        """
        return self.__proxy

    def getProxyList(self):
        """The proxies list getter

        @returns list: The proxies list
        """
        return self.__proxyList

    def getRequestIndex(self):
        """The request index getter

        @returns int: The request index
        """
        return self.__requestIndex

    def getParser(self):
        """The request parser getter

        @returns RequestParser: The request parser
        """
        return self.__parser

    def isSubdomainFuzzing(self):
        """The Subdomain Fuzzing flag getter

        @returns bool: The Subdomain Fuzzing flag
        """
        return self.__subdomainFuzzing

    def setHeaderContent(self, key: str, value: str):
        """The header content setter

        @type key: str
        @param key: The HTTP Header key
        @type value: str
        @param value: The HTTP Header value
        """
        if '$' in value:
            self.__httpHeader['keysCustom'].append(key)
            self.__httpHeader['content'][key] = parseHeaderValue(value)
        else:
            self.__httpHeader['content'][key] = value

    def setProxy(self, proxy: dict):
        """The proxy setter

        @type proxy: dict
        @param proxy: The proxy used in the request
        """
        self.__proxy = proxy

    def setProxyList(self, proxyList: list):
        """The proxy list setter

        @type proxyList: list
        @param proxyList: The list with the proxies used in the requests
        """
        self.__proxyList = proxyList

    def setTimeout(self, timeout: int):
        """The timeout setter

        @type timeout: int
        @param timeout: The request timeout
        """
        self.__timeout = timeout

    def testConnection(self, proxy: bool = False):
        """Test the connection with the target, and raise an exception if couldn't connect (by status code)"""
        try:
            target = self.__parser.getTargetFromUrl()
            response = requests.get(
                target,
                proxies=self.__proxy if proxy else {},
                headers=self.__parser.getHeader(),
                timeout=self.__timeout if self.__timeout else 10 # Default 10 seconds to make a request
            )
            response.raise_for_status()
        except:
            raise RequestException('', target)

    def hasRedirection(self):
        """Test if the connection will have a redirection"""
        self.__parser.setPayload(' ')
        requestParameters = self.__parser.getRequestParameters()
        response = requests.request(
            requestParameters['Method'],
            requestParameters['Url'],
            data=requestParameters['Data'],
            params=requestParameters['Data'],
            headers=requestParameters['Header'],
            proxies=self.__proxy
        )
        if ('[302]' in str(response.history)):
            return True
        return False

    def request(self, payload: str):
        """Make a request and get the response

        @type payload: str
        @param payload: The payload used in the request
        @returns dict: The response data dictionary
        """
        if self.__proxyList and self.__requestIndex%1000 == 0:
            self.__updateProxy()
        self.__parser.setPayload(payload)
        requestParameters = self.__parser.getRequestParameters()
        targetIp = ''
        if self.__subdomainFuzzing:
            try:
                hostname = self.__parser.getPayloadedDomain(requestParameters['Url'])
                targetIp = socket.gethostbyname(hostname)
            except:
                raise RequestException('continue', f"Can't resolve hostname {hostname}")
        try:
            before = time.time()
            response = Response(requests.request(
                requestParameters['Method'],
                requestParameters['Url'],
                data=requestParameters['Data'],
                params=requestParameters['Data'],
                headers=requestParameters['Header'],
                proxies=self.__proxy,
                timeout=self.__timeout
            ))
            timeTaken = (time.time() - before)
        except requests.exceptions.ProxyError:
            raise RequestException('stop', "The actual proxy isn't working anymore.")
        except requests.exceptions.TooManyRedirects:
            raise RequestException(
                'stop' if not self.__subdomainFuzzing else 'continue',
                f"Too many redirects on {requestParameters['Url']}"
            )
        except requests.exceptions.SSLError:
            raise RequestException(
                'stop' if not self.__subdomainFuzzing else 'continue',
                f"SSL couldn't be validated on {requestParameters['Url']}"
            )
        except requests.exceptions.Timeout:
            raise RequestException(
                'stop' if not self.__subdomainFuzzing else 'continue',
                f"Connection to {requestParameters['Url']} timed out"
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException
        ) as e:
            raise RequestException(
                'stop' if not self.__subdomainFuzzing else 'continue',
                f"Failed to establish a new connection to {requestParameters['Url']}, raised by {type(e).__name__}"
            )
        except UnicodeError:
            raise RequestException('continue', f"Invalid hostname {hostname} for HTTP request")
        else:
            self.__requestIndex += 1
            response.setRequestData(
                payload if not self.__subdomainFuzzing else requestParameters['Url'],
                timeTaken,
                self.__requestIndex,
                targetIp
            )
            return response.getResponseDict()

    def handleProxyException(self):
        """Handle with the proxy exception
           If a proxies list is set remove the current proxy and grab another

        @returns bool: A flag to continue or stop the fuzzing tests
        """
        self.__proxy = {}
        if self.__proxyList:
            del self.__proxyList[(self.__requestIndex%1000)%len(self.__proxyList)]
            if self.__proxyList:
                self.__updateProxy()
                return True
        return False

    def __setupHeader(self):
        """Setup the HTTP Header"""
        self.__httpHeader = {
            'content': self.__httpHeader,
            'keysCustom': [],
        }
        for key, value in self.__httpHeader['content'].items():
            self.setHeaderContent(key, value)

    def __updateProxy(self):
        """Set the proxy based on request index"""
        self.setProxy(self.__proxyList[(self.__requestIndex%1000)%len(self.__proxyList)])
