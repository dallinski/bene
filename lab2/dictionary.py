d = {}
print d
d[10] = ("Ten",2222)
d[14] = ("Fourteen",123)
d[11] = ("Eleven",43234)
d[2] = ("Two",1234)
d[13] = ("Thirteen",2345)
d[6] = ("Six",1123)
d[3] = ("Three",323)
d[4] = ("Four",248)
# d[1] = ("One",8765)
d[7] = ("Seven",776)
d[9] = ("Nine",987)
d[8] = ("Eight",5674)
d[5] = ("Five",87654)
print d
print min(d)
print d[min(d)]
print d[min(d)][1]