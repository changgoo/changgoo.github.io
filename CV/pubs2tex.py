from datetime import date
import json
import re
from utf8totex import utf8totex

students = [
    "raileanu",
    "el-badry",
    "vijayan",
    "woorak",
    "kado-fong",
    "mao",
]

_JOURNAL_MAP = {
    "ArXiv e-prints": "ArXiv",
    "The Astronomical Journal": "\\aj",
    "The Astrophysical Journal": "\\apj",
    "The Astrophysical Journal Supplement Series": "\\apjs",
    "Astronomy and Astrophysics": "\\aanda",
    "Galaxies": "MDPI: galaxies",
    "The Journal of Open Source Software": "JOSS",
    "Monthly Notices of the Royal Astronomical Society": "\\mnras",
    "Nature": "\\nature",
    "Nature Astronomy": "\\natureast",
    "Publications of the Astronomical Society of the Pacific": "\\pasp",
    "Publications of the Astronomical Society of Japan": "\\pasj",
}

JOURNAL_SKIP = [
    "VizieR Online Data Catalog",
    "^American Astronomical Society.*",
    "^AAS.*",
    "Astrophysics Source Code Library",
    "Zenodo Software Release",
    "Ph.D. Thesis",
    "Spitzer Proposal",
    "Rediscovering Our Galaxy",
    "The Astronomer's Telegram",
]
JOURNAL_SKIP = [x.lower() for x in JOURNAL_SKIP]

# Lower case journals:
JOURNAL_MAP = {}
for k, v in _JOURNAL_MAP.items():
    JOURNAL_MAP[k.lower()] = v


def format_name(name):
    try:
        last, others = name.split(', ')
        others = ['{0}.'.format(o[0]) for o in others.split()]
        name = "{last}, {first}".format(first=' '.join(others), last=last)

    except ValueError:
        print("couldn't format name '{0}'".format(name))

    return name


def parse_authors(paper_dict, max_authors=4):
    raw_authors = [utf8totex(x) for x in paper_dict['authors']]

    show_authors = raw_authors[:max_authors]

    if any(['chang-goo' in x.lower() for x in show_authors]):
        # Bold my name because it makes the cut to be shown
        names = []
        for name in show_authors:
            if 'chang-goo' in name.lower():
                name = '\\textbf{Kim, Chang-Goo}'
            else:
                for stuname in students:
                    if stuname in name.lower():
                        name = '\\student{' + name +'}'
                        print(name)
#            else:
#                name = format_name(name)
            names.append(name)

        author_tex = '; '.join(names)

        if len(show_authors) < len(raw_authors): # use et al.
            author_tex = author_tex + "~\\textit{et al.}"

    else:
        # Add "incl. CGK" after et al., because I'm buried in the author list
        n_authors = len(raw_authors)
        for i,x in enumerate(raw_authors):
            if 'chang-goo' in x.lower():
                i_author = i+1
        author_tex = "{0}".format(format_name(show_authors[0]))
        author_tex += "~\\textit{et al.}~(incl. \\textbf{CGK}"
        author_tex += "; {}/{})".format(i_author,n_authors)
        print(i_author,n_authors)

    return author_tex


def filter_papers(pubs):
    filtered = []

    for p in pubs:
        if p["pub"] is None:
            continue

        # Skip if the publication is in the skip list:
        if any([re.match(re.compile(pattr), p['pub'].lower())
                for pattr in JOURNAL_SKIP]):
            continue

        if p["pub"].lower() != "arxiv e-prints":
            pub = JOURNAL_MAP.get(p["pub"].strip("0123456789# ").lower(),
                                  None)

            if pub is None:
                print("Journal '{0}' not recognized for paper '{1}' - "
                      " skipping...".format(p['pub'], p['title']))
                continue

        # HACK: hard-coded skip
        if 'astropy problem' in p['title'].lower():
            continue

        filtered.append(p)

    return filtered


def get_paper_items(papers):
    refereeds = []
    preprints = []

    first_refs = []
    secthr_refs = []
    other_refs = []
    for paper in papers:
        authors = parse_authors(paper)
        entry = authors

        # Skip if the publication is in the skip list:
        if any([re.match(re.compile(pattr), paper['pub'].lower())
                for pattr in JOURNAL_SKIP]):
            continue

        if paper["doi"] is not None:
            title = "\\doiform{{{0}}}{{{1}}}".format(paper["doi"],
                                                 utf8totex(paper["title"]))
        else:
            title = "\\textit{{{0}}}".format(utf8totex(paper["title"]))
        if '<SUB>' in title:
            title=title.replace('<SUB>','${}_{').replace('</SUB>','}$')
            print(title)
        entry += ", " + title

        if paper["pub"] not in [None, "ArXiv e-prints", "arXiv e-prints"]: # HACK
            pub = JOURNAL_MAP.get(paper["pub"].strip("0123456789# ").lower(),
                                  None)

            if pub is None:
                print("Journal '{0}' not recognized for paper '{1}' - "
                      " skipping...".format(paper['pub'], paper['title']))
                continue

            entry += ", " + pub
            is_preprint = False

        else:
            is_preprint = True

        if paper["volume"] is not None:
            entry += ", \\textbf{{{0}}}".format(paper["volume"])

        if paper["page"] is not None:
            entry += ", {0}".format(paper["page"])

        if paper['pubdate'] is not None:
            entry += ", {0}".format(paper['pubdate'].split('-')[0])

        if paper["arxiv"] is not None:
            entry += " (\\arxiv{{{0}}})".format(paper["arxiv"])

        if paper["citations"] > 1:
            entry += (" [\\href{{{0}}}{{{1} citations}}]"
                      .format(paper["url"], paper["citations"]))

        if is_preprint:
            preprints.append(entry)

        else:
            refereeds.append(entry)
            myname = "Chang-Goo"
            if myname in paper["authors"][0]:
                first_refs.append(entry)
            elif (len(paper["authors"]) > 1) and (myname in paper["authors"][1]):
                    secthr_refs.append(entry)
            #elif (len(paper["authors"]) > 2) and (myname in paper["authors"][2]):
            #        secthr_refs.append(entry)
            else:
                other_refs.append(entry)


    # Now go through and add the \item and numbers:
    for corpus in [preprints, refereeds]:
        for i, item in enumerate(corpus):
            num = len(corpus) - i
            corpus[i] = ("\\item[{" + #\\color{deemph}\\scriptsize" +
                         str(num) + ".}]" + item)

    nums = range(len(refereeds)+1)[::-1]
    j=0
    for corpus in [first_refs, secthr_refs, other_refs]:
        for i, item in enumerate(corpus):
            #num = len(corpus) - i
            num = nums[j]
            corpus[i] = ("\\item[{" + #\\color{deemph}\\scriptsize" +
                         str(num) + ".}]" + item)
            j+=1


    return refereeds, preprints, first_refs, secthr_refs, other_refs


if __name__ == '__main__':
    from os import path
    if not path.exists('pubs.json'):
        raise FileNotFoundError("File 'pubs.json' not found - run get_pubs.py "
                                "before running this script.")

    with open("pubs.json", "r") as f:
        pubs = json.loads(f.read())

    papers = filter_papers(pubs)
    refs, unrefs, first_refs, secthr_refs, other_refs = get_paper_items(papers)

    # Compute citation stats
    nref = len(refs)
    cites = sorted((p["citations"] for p in papers), reverse=True)
    ncitations = sum(cites)

    # Compute for specific conditions
    myname = "Chang-Goo"
    nfirst = 0
    nsecthr = 0
    cites_first = []
    cites_secthr = []
    for p in papers:
        if myname in p["authors"][0]:
            nfirst += 1
            cites_first.append(p["citations"])
        elif len(p["authors"]) > 1:
            if (myname in p["authors"][1]):
                nsecthr += 1
                cites_secthr.append(p["citations"])
        elif len(p["authors"]) > 2:
            if myname in p["authors"][2]:
                nsecthr += 1
                cites_secthr.append(p["citations"])
    cites_first = sorted(cites_first, reverse=True)
    ncitations_first = sum(cites_first)
    cites_secthr = sorted(cites_secthr, reverse=True)
    ncitations_secthr = sum(cites_secthr)
    hindex = sum(c > i for i, c in enumerate(cites))
    hindex_first = sum(c > i for i, c in enumerate(cites_first))

    #summary = (("Metrics (as of \\textit{{{0}}}) --- refereed: {1}"
    #            " ({2} as the first/{3} as the second or third author) \\\\ "
    #            "citations: {4} ({5}/{6}) --- h-index: {7} ({8})")
    #           .format(date.today(), nref, nfirst, nsecthr,
    #                   ncitations, ncitations_first, ncitations_secthr,
    #                   hindex, hindex_first))

    summary = (("Publication metrics (based on NASA ADS, as of textit{{{0}}}): \\\\ "
                "refereed: {1} --- citations: {4} --- h-index: {7}")
               .format(date.today(), nref, nfirst, nsecthr,
                       ncitations, ncitations_first, ncitations_secthr,
                       hindex, hindex_first))
    summary_1st = ((" (first author papaers: {2} --- citations: {5} --- h-index: {8})")
               .format(date.today(), nref, nfirst, nsecthr,
                       ncitations, ncitations_first, ncitations_secthr,
                       hindex, hindex_first))
    print("-"*32)
    print("Summary:")
    print(summary)
    print(summary_1st)

    with open("summary.tex", "w") as f:
        f.write(summary)

    with open("summary_1st.tex", "w") as f:
        f.write(summary_1st)

    with open("pubs_ref.tex", "w") as f:
        f.write("\n\n".join(refs))

    with open("pubs_ref_1st.tex", "w") as f:
        f.write("\n\n".join(first_refs))

    with open("pubs_ref_2nd.tex", "w") as f:
        f.write("\n\n".join(secthr_refs))

    with open("pubs_ref_co.tex", "w") as f:
        f.write("\n\n".join(other_refs))

    with open("pubs_arxiv.tex", "w") as f:
        f.write("\n\n".join(unrefs))
