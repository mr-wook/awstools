#!/bin/env python3

if True:
    import boto3
    from   collections import OrderedDict
    import os
    import re
    import sys
    import time

    # import wookutil3


class Gather:
    DIR_REX = r"/(?P<prefix>.*?)/old(?P<suffix>$|/)"
    def __init__(self, top, **kwa):
        self._top = top
        self._excluded_exts = kwa.get('excluded_exts', [ ".cin", ".dpx", ".exr", ".o" ])
        self._excluded_dirs = kwa.get('excluded_dirs', [ "old" ])
        self._edrexs = [ ]
        for dirnm in self._excluded_dirs:
            rex = re.compile(f"/(?P<prefix>.*?)/{dirnm}(?P<suffix>$|/)")
            self._edrexs.append(rex)
        # print(f"Gather.init: top={top}")
        # os.chdir(top)
        self._work = self.findwork(top)

    def __iter__(self):
        for fp in self._work:
            yield fp

    def excluded_dir(self, nm):
        for rex in self._edrexs:
            if rex.match(nm):
                return True
        return False

    def findwork(self, top):
        works = [ ]
        for dirnm, stuff, flist in os.walk(top):
            # print(f"{dirnm}/{fn}")
            l_top = len(top)
            if dirnm.startswith(top):
                dirnm = dirnm[l_top + 1:]
            if self.excluded_dir(dirnm):
                continue
            for fn in flist:
                ext = os.path.splitext(fn)[-1]
                if ext in self._excluded_exts:
                    continue
                # print(f"Gather.init: fn: {fn}")
                if dirnm:
                    work = f"{dirnm}/{fn}"
                else:
                    work = fn
                # print(f"Gather: work={work}") ; time.sleep(0.25)
                works.append(work)
        works.sort()
        return works

    @property
    def work(self):
        return self._work
    

if __name__ == "__main__":
    class App:
        def __init__(self, bucket, key_top, src_top):
            self._bucket, self._key_top, self._src_top = bucket, key_top, src_top
            self._gather = Gather(src_top)
            self._map = self._load_map()
            self._done = [ ]
            self._s3 = boto3.client('s3')

        def __iter__(self):
            for fp in self._map:
                yield fp

        def __len__(self):
            return len(self._done)

        def __getitem__(self, i):
            return self._done[i]

        def clock_time(self, seconds):
            hours = int(seconds // 3600)
            seconds = seconds % 3600
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{hours}:{minutes:02d}:{seconds:02d}"

        def human_size(self, n):
            def right_str(n, mag, label):
                v = n / mag
                s = f"{v:.2f} {label}"
                return s
            KB = 1024.0
            MB = KB * 1024
            GB = MB * 1024
            TB = GB * 1024
            if n > TB:
                return right_str(n, TB, "TB")
            if n > GB:
                return right_str(n, GB, "GB")
            if n > MB:
                return right_str(n, MB, "MB")
            elif n > KB:
                return right_str(n, KB, "KB")
            return f"{n} bytes"

        def _load_map(self):
            mapping = OrderedDict()
            for fp in self._gather:
                b_str = f'{self._key_top}/{fp}'
                if ' ' in b_str:
                    b_str.replace(" ", "_")
                mapping[fp] = b_str
                # print(f"mapping[{fp}]: {mapping[fp]}") ; time.sleep(0.25)
            return mapping

        def save(self, fp):
            tfp = f"{self._src_top}/{fp}"
            # print(f"Saving {tfp}") ; time.sleep(0.125)
            try:
                rc = self._s3.upload_file(tfp, self._bucket, self._map[fp])
            except Exception as e:
                print(f"ERROR: {str(e)} for {tfp} -- bad link?")
                return False
            self._done.append(( tfp, self.size(tfp) ))
            # print(f"Saved {fp} --> {self._bucket}:{self._map[fp]}") ; time.sleep(0.125)
            return True

        def size(self, fp):
            try:
                sz = os.stat(fp)[6]
            except Exception as e:
                print(f"os.stat({fp}) failed")
                return 0
            return sz

        @property
        def bucket(self):
            return self._bucket
        
        @property
        def done_size(self):
            return sum([tup[-1] for tup in self._done])

        @property
        def gather(self):
            return self._gather

        @property
        def work(self):
            return self._gather.work


    pname, *args = sys.argv
    if len(args) < 3:
        print("Not enough args <bucket> <top-key> <top-src-dir>")
        sys.exit(1)
    app = App(*args)
    step = 100
    start = time.time()
    for work in app:
        app.save(work)
        if len(app) % step == 0:
            print(f"{app[-1][0]} [{len(app)}]")
    end = time.time()
    elapsed = end - start
    total_xfer = app.done_size
    bps = total_xfer / elapsed
    bpU = app.human_size(bps)
    print(f"Total files transferred: {len(app)}; Total data transferred: {app.human_size(total_xfer)}; {elapsed:.2f} seconds; ({bpU}/sec)")
