var __encode = 'jsjiami.com', _a = {},
    _0xb483 = ["\x5F\x64\x65\x63\x6F\x64\x65", "\x68\x74\x74\x70\x3A\x2F\x2F\x77\x77\x77\x2E\x73\x6F\x6A\x73\x6F\x6E\x2E\x63\x6F\x6D\x2F\x6A\x61\x76\x61\x73\x63\x72\x69\x70\x74\x6F\x62\x66\x75\x73\x63\x61\x74\x6F\x72\x2E\x68\x74\x6D\x6C"];
(function (_0xd642x1) {
    _0xd642x1[_0xb483[0]] = _0xb483[1]
})(_a);
var __Oxdef43 = ["\x6C\x65\x6E\x67\x74\x68", "\x73\x75\x62\x73\x74\x72\x69\x6E\x67", "", "\x63\x68\x61\x72\x41\x74", "\x2B", "\x20", "\x25", "\x30\x78", "\x63\x68\x61\x72\x43\x6F\x64\x65\x41\x74", "\x66\x72\x6F\x6D\x43\x68\x61\x72\x43\x6F\x64\x65", "\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4A\x4B\x4C\x4D\x4E\x4F\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5A\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6A\x6B\x6C\x6D\x6E\x6F\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7A\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x2B\x2F\x3D", "\x69\x6E\x64\x65\x78\x4F\x66", "\x6A\x6F\x69\x6E", "\x75\x6E\x64\x65\x66\x69\x6E\x65\x64", "\x6C\x6F\x67", "\u5220\u9664", "\u7248\u672C\u53F7\uFF0C\x6A\x73\u4F1A\u5B9A", "\u671F\u5F39\u7A97\uFF0C", "\u8FD8\u8BF7\u652F\u6301\u6211\u4EEC\u7684\u5DE5\u4F5C", "\x6A\x73\x6A\x69\x61", "\x6D\x69\x2E\x63\x6F\x6D"];

function getVideoInfo(_0x38afx2) {
    string = _0x38afx2[__Oxdef43[0x1]](8, _0x38afx2[__Oxdef43[0x0]]);
    substr = base64_decode(string);
    return UrlDecode(substr[__Oxdef43[0x1]](8, substr[__Oxdef43[0x0]] - 8))
}

function UrlDecode(_0x38afx4) {
    var _0x38afx5 = __Oxdef43[0x2];
    for (var _0x38afx6 = 0; _0x38afx6 < _0x38afx4[__Oxdef43[0x0]]; _0x38afx6 += 1) {
        var _0x38afx7 = _0x38afx4[__Oxdef43[0x3]](_0x38afx6);
        if (_0x38afx7 === __Oxdef43[0x4]) {
            _0x38afx5 += __Oxdef43[0x5]
        } else {
            if (_0x38afx7 === __Oxdef43[0x6]) {
                var _0x38afx8 = _0x38afx4[__Oxdef43[0x1]](_0x38afx6 + 1, _0x38afx6 + 3);
                if (parseInt(__Oxdef43[0x7] + _0x38afx8) > 0x7f) {
                    _0x38afx5 += decodeURI(__Oxdef43[0x6] + _0x38afx8.toString() + _0x38afx4[__Oxdef43[0x1]](_0x38afx6 + 3, _0x38afx6 + 9).toString());
                    _0x38afx6 += 8
                } else {
                    _0x38afx5 += AsciiToString(parseInt(__Oxdef43[0x7] + _0x38afx8));
                    _0x38afx6 += 2
                }
            } else {
                _0x38afx5 += _0x38afx7
            }
        }
    }
    ;
    return _0x38afx5
}

function StringToAscii(_0x38afxa) {
    return _0x38afxa[__Oxdef43[0x8]](0).toString(16)
}

function AsciiToString(_0x38afxc) {
    return String[__Oxdef43[0x9]](_0x38afxc)
}

function base64_decode(_0x38afxe) {
    var _0x38afxf = __Oxdef43[0xa];
    var _0x38afx10, _0x38afx11, _0x38afx12, _0x38afx13, _0x38afx14, _0x38afx15, _0x38afx16, _0x38afx17, _0x38afx6 = 0,
        _0x38afx18 = 0, _0x38afx19 = __Oxdef43[0x2], _0x38afx1a = [];
    if (!_0x38afxe) {
        return _0x38afxe
    }
    ;_0x38afxe += __Oxdef43[0x2];
    do {
        _0x38afx13 = _0x38afxf[__Oxdef43[0xb]](_0x38afxe[__Oxdef43[0x3]](_0x38afx6++));
        _0x38afx14 = _0x38afxf[__Oxdef43[0xb]](_0x38afxe[__Oxdef43[0x3]](_0x38afx6++));
        _0x38afx15 = _0x38afxf[__Oxdef43[0xb]](_0x38afxe[__Oxdef43[0x3]](_0x38afx6++));
        _0x38afx16 = _0x38afxf[__Oxdef43[0xb]](_0x38afxe[__Oxdef43[0x3]](_0x38afx6++));
        _0x38afx17 = (_0x38afx13 << 18 | _0x38afx14 << 12 | _0x38afx15 << 6 | _0x38afx16);
        _0x38afx10 = (_0x38afx17 >> 16) & 0xff;
        _0x38afx11 = (_0x38afx17 >> 0x8) & 0xff;
        _0x38afx12 = (_0x38afx17 & 0xff);
        if (_0x38afx15 == 64) {
            _0x38afx1a[_0x38afx18++] = String[__Oxdef43[0x9]](_0x38afx10)
        } else {
            if (_0x38afx16 == 64) {
                _0x38afx1a[_0x38afx18++] = String[__Oxdef43[0x9]](_0x38afx10, _0x38afx11)
            } else {
                _0x38afx1a[_0x38afx18++] = String[__Oxdef43[0x9]](_0x38afx10, _0x38afx11, _0x38afx12)
            }
        }
    } while (_0x38afx6 < _0x38afxe[__Oxdef43[0x0]]);
    ;_0x38afx19 = _0x38afx1a[__Oxdef43[0xc]](__Oxdef43[0x2]);
    return _0x38afx19
};
;(function (_0x38afx1b, _0x38afx1c, _0x38afx1d, _0x38afx1e, _0x38afx1f, _0x38afx20) {
    _0x38afx20 = __Oxdef43[0xd];
    _0x38afx1e = function (_0x38afx21) {
        if (typeof alert !== _0x38afx20) {
            alert(_0x38afx21)
        }
        ;
        if (typeof console !== _0x38afx20) {
            console[__Oxdef43[0xe]](_0x38afx21)
        }
    };
    _0x38afx1d = function (_0x38afx22, _0x38afx1b) {
        return _0x38afx22 + _0x38afx1b
    };
    _0x38afx1f = _0x38afx1d(__Oxdef43[0xf], _0x38afx1d(_0x38afx1d(__Oxdef43[0x10], __Oxdef43[0x11]), __Oxdef43[0x12]));
    try {
        _0x38afx1b = __encode;
        if (!(typeof _0x38afx1b !== _0x38afx20 && _0x38afx1b === _0x38afx1d(__Oxdef43[0x13], __Oxdef43[0x14]))) {
            _0x38afx1e(_0x38afx1f)
        }
    } catch (e) {
        _0x38afx1e(_0x38afx1f)
    }
})({})

// var urlString = "BycPgAWcQnljUGdBV2NodHRwczovL2ZmLnFpZnVkYS5jb20vZ2V0bTN1OD91cmw9aHR0cHM6Ly92aXAubHotY2RuMTMuY29tLzIwMjMwODA4LzE2MDc3XzI4MWJlZDNjL2luZGV4Lm0zdThCeWNQZ0FXYw=="
// var player_aaaa={"flag":"play","encrypt":3,"trysee":0,"points":0,"link":"\/vodplay\/102927-1-1.html","link_next":"\/vodplay\/102927-3-2.html","link_pre":"","vod_data":{"vod_name":"\u4e27\u5c38\u5b87\u5b99","vod_actor":"\u674e\u65bd\u541f,\u5362\u6d2a\u54f2,\u6734\u5a1c\u83b1,\u6591\u6591,??,???,Yiombi Jonathan,Patricia Yiombi,\u6d2a\u8bda\u4f51,\u91d1\u73cd\u8363","vod_director":"","vod_class":"\u771f\u4eba\u79c0,\u65e5\u97e9\u7efc\u827a"},"vod_title":"%E4%B8%A7%E5%B0%B8%E5%AE%87%E5%AE%99","vod_pic_thumb":"","vod_title_name":"%E7%AC%AC01%E9%9B%86","url":"oNEsgfdCTGZpxisXqj57afOYo3roo00ois67XnzPzxyIjsEVYtecX1G3mAJOndC5HJTUUWyEQFIBXoo00ojoo00oNngwnm9BDgO0O0OO0O0O","url_next":"oNEsgfdCTGZpxisXqj57afOYo3roo00ois67XnzPzxyIjsHnvV4tuRO1l4Jjo5wYqG2aAkvu5HTbojT1IKeMjOYNYAO0O0OO0O0O","from":"lzm3u8","server":"no","note":"","id":"102927","sid":3,"nid":1}
// url = getVideoInfo(urlString)
// console.log(url)