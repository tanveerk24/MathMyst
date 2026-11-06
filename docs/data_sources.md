# Seed data provenance and interpretation

Sources were checked on **6 November 2026**. This is a small educational catalog,
not a complete history of mathematical research. An absent relationship means
**not recorded in this dataset**, not that research does not exist.

There are 10 problems, 10 mathematicians and 17 contribution rows. A contribution
row records one person's involvement in one research work. Consequently, the two
authors of a paper can have separate rows, and a person can have several distinct
papers on the same problem. Counts measure **recorded rows**, not unique papers,
citations, or the merit of a mathematician.

All `significance_score` values are **fictional teaching ratings** assigned for
aggregate-query practice. They are not sourced historical measurements. Country
labels describe a broad country of origin using modern names, rather than every
citizenship or institutional affiliation. Three birth dates are deliberately NULL.

## Every contribution and its evidence

The IDs below match `database/seed.sql`. Paper dates use first public preprint
years when an arXiv preprint is cited; otherwise they use publication years.

| ID | Person / problem | Research work and scope | Source |
|---|---|---|---|
| 1 | Riemann / Riemann Hypothesis, 1859 | Zeta-function paper containing the hypothesis. | [Clay's manuscript collection](https://www.claymath.org/collections/riemanns-1859-manuscript/) |
| 2 | Wiles / Fermat, 1995 | The main modularity paper establishing the theorem. | [Original Annals article](https://annals.math.princeton.edu/1995/141-3/p01) |
| 3 | Wiles / Fermat, 1995 | Joint Hecke-algebra paper supplying a proof ingredient; distinct from ID 2. | [Taylor–Wiles original paper](https://staff.fnwi.uva.nl/a.l.kret/Galoistheorie/taylor-wiles.pdf) |
| 4 | Taylor / Fermat, 1995 | Coauthor of the same Hecke-algebra paper as ID 3. | [Original paper](https://staff.fnwi.uva.nl/a.l.kret/Galoistheorie/taylor-wiles.pdf) |
| 5 | Tao / Collatz, 2019 | Almost-all-orbits result in logarithmic density; **not the full conjecture**. | [Author's preprint](https://arxiv.org/abs/1909.03562) |
| 6 | Tao / Goldbach, 2012 | Five-prime result for odd numbers; **related weak variant**, not binary Goldbach. | [Author's preprint](https://arxiv.org/abs/1201.6656) |
| 7 | Tao / Navier–Stokes, 2014 | Blowup for an **averaged equation**, illustrating a barrier; not the original equation. | [Author's preprint](https://arxiv.org/abs/1402.0290) |
| 8 | Tao / Twin Prime, 2014 | Participation in Polymath8b's bounded-gap work; not a proof that the gap is two. | [Tao's author announcement](https://terrytao.wordpress.com/2014/07/20/variants-of-the-selberg-sieve-and-bounded-intervals-containing-many-primes/comment-page-1/) and [collective preprint](https://arxiv.org/abs/1407.4897) |
| 9 | Perelman / Poincaré, 2002 | Ricci-flow entropy paper; first of three distinct preprints. | [Original preprint](https://arxiv.org/abs/math/0211159) |
| 10 | Perelman / Poincaré, 2003 | Ricci flow with surgery. | [Original preprint](https://arxiv.org/abs/math/0303109) |
| 11 | Perelman / Poincaré, 2003 | Finite extinction-time argument. | [Original preprint](https://arxiv.org/abs/math/0307245) |
| 12 | Appel / Four Color, 1977 | Part I: discharging. | [Original paper](https://projecteuclid.org/journals/illinois-journal-of-mathematics/volume-21/issue-3/Every-planar-map-is-four-colorable-Part-I-Discharging/10.1215/ijm/1256049011.pdf) |
| 13 | Haken / Four Color, 1977 | Coauthor of the same Part I as ID 12. | [Original paper](https://projecteuclid.org/journals/illinois-journal-of-mathematics/volume-21/issue-3/Every-planar-map-is-four-colorable-Part-I-Discharging/10.1215/ijm/1256049011.pdf) |
| 14 | Appel / Four Color, 1977 | Part II: reducibility, also coauthored with John Koch. | [Original Part II](https://projecteuclid.org/journals/illinois-journal-of-mathematics/volume-21/issue-3/Every-planar-map-is-four-colorable-Part-II-Reducibility/10.1215/ijm/1256049012.full) and [Haken's ICM account](https://www.mathunion.org/fileadmin/ICM/Proceedings/ICM1978.2/ICM1978.2.ocr.pdf) |
| 15 | Haken / Four Color, 1977 | Coauthor of the same Part II as ID 14. | [Haken's own ICM account](https://www.mathunion.org/fileadmin/ICM/Proceedings/ICM1978.2/ICM1978.2.ocr.pdf) |
| 16 | Maynard / Twin Prime, 2013 | Multidimensional sieve for bounded prime gaps; preprint 2013, journal 2015. | [Original preprint](https://arxiv.org/abs/1311.4600) and [Annals article](https://annals.math.princeton.edu/2015/181-1/p07) |
| 17 | Zhang / Twin Prime, 2013 | Bounded prime gaps; result submitted 2013, journal 2014. | [Original Annals article and milestones](https://annals.math.princeton.edu/2014/179-3/p07) |

The Polymath article has collective authorship. ID 8 records Tao's participation,
supported by his first-person announcement; it does not assign sole credit.
Likewise, omitting John Koch from our deliberately limited people table does not
deny his coauthorship of Part II. The descriptions above explicitly preserve it.

## Problems, years, status and prize meaning

`proposed_year` is a compact historical teaching attribute. It cannot express an
uncertain range or distinguish every predecessor formulation. In particular:

- Riemann: 1859, documented by the [original manuscript collection](https://www.claymath.org/collections/riemanns-1859-manuscript/).
- Goldbach: 1742 correspondence; the seed represents the **binary/strong** conjecture. See the historical discussion in [Helfgott's ternary Goldbach work](https://arxiv.org/abs/1312.7748).
- Collatz: conventionally 1937, as recorded by [NIST](https://xlinux.nist.gov/dads/HTML/CollatzProblem.html); the exact historical development is more nuanced.
- Twin Prime: 1849 refers to de Polignac's general prime-gap conjecture, whose gap-two case is the twin-prime problem. See the [French Academy's discussion](https://www.academie-sciences.fr/pdf/lettre/lettre33.pdf).
- Fermat: approximately 1637 for the margin note; see the [Abel Prize historical account](https://abelprize.no/sites/default/files/2021-04/Popular_version_Bellos_story_en_2016_A.Wiles_.pdf).
- P versus NP: 1971 for the modern complexity formulation; see [Clay's problem page](https://www.claymath.org/millennium/p-vs-np/).
- Poincaré: 1904, recorded in the [Clay Millennium catalog](https://www.claymath.org/Millennium%20Problems/).
- Four Color: 1852, when Guthrie's question reached De Morgan; see the [University of St Andrews historical account](https://mathshistory.st-andrews.ac.uk/HistTopics/The_four_colour_theorem/).
- Birch and Swinnerton-Dyer: 1965 refers to the published conjecture, developed in the early 1960s; see the [research discussion](https://arxiv.org/abs/2105.10805).
- Navier–Stokes: **2000 refers to the Clay prize formulation**, not the origin of the equations or the regularity question, both of which are older. See the [Millennium announcement](https://www.claymath.org/Millennium%20Problems/) and [official problem description](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf).

Clay's catalog verifies the listed Millennium problems' status and the allocation
of USD 1 million per problem. The seed records active prize amounts; Poincaré's
closed award is represented by `has_prize = FALSE` and zero, rather than suggesting
an available prize. Zero means **no prize recorded here**, not proof that no
organization has ever offered a reward. Goldbach, Collatz and Twin Prime remain
unsolved in the sense stated in the cited research; partial variants are kept
separate from full solutions.

## Biographical references

- Riemann: [University of California, Berkeley biography](https://math.berkeley.edu/~robin/Riemann/) (birth date and German origin).
- Wiles: [Princeton faculty biography](https://dof.princeton.edu/people/andrew-john-wiles).
- Tao: [his UCLA first-person biography](https://www.math.ucla.edu/~tao/whoami).
- Perelman: [University of St Andrews biography](https://mathshistory.st-andrews.ac.uk/Biographies/Perelman/).
- Appel: [University of St Andrews biography](https://mathshistory.st-andrews.ac.uk/Biographies/Appel/).
- Haken: [Celebratio Mathematica's collected works](https://celebratio.org/Haken_W/cover/708/) and [family obituary](https://www.legacy.com/us/obituaries/news-gazette/name/wolfgang-haken-obituary?id=36782655).
- Maynard, Zhang and Taylor have no birth date asserted; their research fields are supported by the original papers above.
- Ramanujan: [University of St Andrews biography](https://mathshistory.st-andrews.ac.uk/Biographies/Ramanujan/). His lack of contribution rows is intentional; it is not a claim that he made no mathematical contributions.

The dataset intentionally leaves P versus NP and Birch and Swinnerton-Dyer without
contribution rows so that LEFT JOIN and NOT EXISTS have useful demonstrations.
It is not necessary to invent a link merely to populate every parent record.
