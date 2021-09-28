# -*- coding: utf-8 -*-
# Author: Chmouel Boudjnah <chmouel@chmouel.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import glob
import os.path


def generate_section(ifp, allf):
    for x in sorted(allf):
        x = os.path.basename(x)
        if x == "index.md":
            continue
        ss = x

        sp = x.replace("_-_", "_").split("-")
        if len(sp) == 3 and sp[1].startswith(sp[0]):
            ss = sp[0] + "-" + sp[2]

        ss = ss.replace("_", " ").replace("-", " / ").replace(".md", "")
        ifp.write(f"* [{ss}]({x})\n\n")


def generate_index(docdir):
    with open(os.path.join(docdir, "index.md"), 'w') as ifp:
        ifp.write("# TR Workouts as Markdown Files\n")
        ifp.write("\n")

        allc = [x for x in glob.glob(os.path.join(docdir, "*.md"))
                if 'Triathlon' not in x]
        allt = glob.glob(os.path.join(docdir, "*Triathlon*.md"))

        ifp.write("## Cycling \n\n")

        ifp.write("### Base training \n\n")
        generate_section(ifp, [x for x in allc if "Base" in x])

        ifp.write("### Build training \n\n")
        generate_section(ifp, [x for x in allc if "Build" in x])

        others = ([x for x in allc if "Build" not in x and
                   'Base' not in x and not x.endswith('index.md')])

        ifp.write("### Speciality training \n\n")
        generate_section(ifp, others)

        ifp.write("## Triathlon \n\n")

        for cat in ["Full", "Half", "Olympic", "Sprint"]:
            ifp.write(f"### {cat}\n\n")
            generate_section(ifp, [x for x in allt if f"{cat}_" in x])

        ifp.write("___\n<sup>This is copyrighted by TR please "
                  "[subscribe](http://trainerroad.com/sign-up) to it ! "
                  "</sup>\n")
