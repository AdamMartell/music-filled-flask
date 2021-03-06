#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
try:
    from urllib.request import urlopen
    from urllib.parse import parse_qs, urlparse
except:
    from urllib import urlopen
    from urlparse import parse_qs, urlparse

class UnknownQualityGroup(Exception):
    """Raised when an unknown quality group is passed."""
    pass

class YouTubeAPIError(Exception):
    """Raised when the YouTube API returns unknown data."""
    pass

class InvalidItagError(Exception):
    """Raised when we get a locally unknown itag."""
    pass

class YTURL(object):
    """Get direct URLs to YouTube videos."""
    def __init__(self, quality, url, test=False):
        self.itags = self.getDefaultItagQualityOrder(test)
        self.quality = quality
        self.url = url
        self.videoIDLength = 11

    def getDefaultItagQualityOrder(self, test=False):
        """Return itags in order of quality preference."""
        itags = {
        #   itag   v-dimensions v-bitrate a-bitrate a-samplerate
            "5":  [400*240,     0.25,     64,       22.05],
            "6":  [480*270,     0.8,      64,       22.05],
            "13": [176*144,     0.5,      64,       22.05],
            "17": [176*144,     2,        64,       22.05],
            "18": [640*360,     0.5,      128,      44.1],
            "22": [1280*720,    2.9,      96,       44.1],
            "34": [640*360,     0.5,      128,      44.1],
            "35": [854*480,     1,        128,      44.1],
            "36": [320*240,     0.17,     38,       44.1],
            "37": [1920*1080,   2.9,      152,      44.1],
            "38": [4096*3072,   5,        152,      44.1],
            "43": [640*360,     0.5,      128,      44.1],
            "44": [854*480,     1,        128,      44.1],
            "45": [1280*720,    2,        192,      44.1],
            "46": [1920*1080,   2,        192,      44.1],
        }

        if test:
            # Python 3 changed the way sorting works for functionally identical
            # objects. We add the itag at the end to make them unique so that
            # the sorting order is always the same, which means we can easily
            # test that the function works as expected. This is not required in
            # normal use, because we don't care which order identical itags are
            # returned in relative to each other.
            for itag in itags:
                itags[itag].append(itag)

        return sorted(itags, reverse=True, key=lambda x: itags[x])

    def stripToVideoID(self, url):
        """Strip URL to the video ID contained."""
        try:
            parsed = urlparse(url).query
            return parse_qs(parsed)["v"][0][:self.videoIDLength]
        except (IndexError, ValueError, KeyError):
            return url.split("/")[-1][:self.videoIDLength]

    def getAvailableVideoItags(self, videoID, f=None):
        """Return available itags and their associated URLs as a list."""
        if f == None:
            url = "http://youtube.com/get_video_info?hl=en&video_id=" + videoID
            res = urlopen(url)
        else:
            res = f
        res = parse_qs(res.read().decode("utf8"))
        try:
            for fmt in res["url_encoded_fmt_stream_map"][0].split(","):
                fmt = parse_qs(fmt)
                yield (
                    fmt["itag"][0],
                    "%s&signature=%s" % (fmt["url"][0], fmt["sig"][0])
                )
        except (KeyError, IndexError):
            raise YouTubeAPIError(res["reason"][0])

    def getDesiredItagOrder(self, desiredItag):
        """Return the desired itag sorting."""
        if desiredItag not in self.itags:
            raise InvalidItagError(desiredItag)

        return list(zip(*sorted(
            enumerate(self.itags),
            key=lambda x: abs(self.itags.index(desiredItag) - x[0]))
        ))[1]

    def parseQualityGroup(self, name):
        """Parse string based quality groups into their itag equivalents."""
        if name == "low":
            return self.itags[-1]
        elif name == "medium":
            return self.itags[int(len(self.itags)/2)]
        elif name == "high":
            return self.itags[0]
        else:
            try:
                int(name)
                return name
            except ValueError:
                raise UnknownQualityGroup(name)

    def getURL(self):
        """Get an itag and its corresponding URL for a YouTube video."""
        itag = self.parseQualityGroup(self.quality)
        videoID = self.stripToVideoID(self.url)
        availableItags = dict(self.getAvailableVideoItags(videoID))
        desiredItagOrder = self.getDesiredItagOrder(itag)
        desiredItag = [ x for x in desiredItagOrder if x in availableItags ]
        try:
            return desiredItag[0], availableItags[desiredItag[0]]
        except IndexError:
            return None, None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-q", "--quality",
        help='specify quality, can be "low", "high", or an itag (see http://goo.gl/uEIuR)',
        default="medium"
    )
    parser.add_argument(
        "url",
        metavar="videoID/url",
        help="a YouTube url (or bare video ID)"
    )
    args = parser.parse_args()

    y = YTURL(args.quality, args.url)
    itag, url = y.getURL()
    if not itag:
        print("No local itags available.", file=sys.stderr)
        sys.exit(1)

    print("Using itag %s." % itag, file=sys.stderr)
    print(url)
