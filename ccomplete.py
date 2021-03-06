from CComplete.tokenizer import Tokenizer
from CComplete.includescanner import IncludeScanner
import re, bisect, time

class CComplete:
    def __init__(self, cachesize = 500, cachepath = "/tmp"):
        self.cachesize = cachesize
        self.T = Tokenizer(cachepath, cachesize)
        self.I = IncludeScanner()
        self.tokens = {}
        self.functiontokens = {}

    def add_tokens(self, tokens):
        for tokenname in tokens:
            token=tokens[tokenname]
            if tokenname in self.tokens:
                self.tokens[tokenname] = Tokenizer.best_match([self.tokens[tokenname], token])
            else:
                self.tokens[tokenname] = token

    def is_valid(self, filename, basepaths = [], syspaths = [], extra_files=[]):
        files = self.I.scan_recursive(filename, basepaths, syspaths)
        for file in extra_files:
            if file not in files:
                files.append(file)
        return self.T.files_valid(files)

    def load_file(self, filename, basepaths = [], syspaths = [], extra_files=[], progress = None):
        t=time.clock()
        self.files = self.I.scan_recursive(filename, basepaths, syspaths)
        t=time.clock()-t
        print("Scanning for includes took: %fs" % t)
        for file in extra_files:
            if file not in self.files:
                self.files.append(file)
        self.T.set_cache_size(max(self.cachesize, len(self.files)))
        self.tokens = {}
        self.functiontokens = {}
        self.sortedtokens = []
        total = len(self.files)
        i=1
        t=time.clock()-t
        for file in self.files:
            if progress:
                progress(i, total)
                i+=1
            tokens, functokens = self.T.scan_file(file)
            self.add_tokens(tokens)
            self.functiontokens[file] = functokens
        t=time.clock()-t
        print("Scanning for tokens took: %fs" % t)
        self.sortedtokens = [x for x in self.tokens.keys()]
        self.sortedtokens.sort()
        rem = self.T.clean_cache(set(self.files))
        print("Removed %d entries" % rem)
        print("Done loading, %d files" % len(self.files))

    def search_tokens(self, prefix):
        pos=bisect.bisect_left(self.sortedtokens, prefix)
        results=[]
        while pos < len(self.sortedtokens):
            if self.sortedtokens[pos].startswith(prefix):
                results.append(self.tokens[self.sortedtokens[pos]])
            else:
                break
            pos+=1
        return results
