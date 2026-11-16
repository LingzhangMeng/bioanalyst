# 10 — Biological interpretation and literature evidence (S6)

Interpretation is where statistical output becomes a scientific claim. The job is not to make the
result interesting — it is to state exactly how much the data support.

Deliverables: `13_Reports/Findings_Ledger.csv` (one row per claim), `11_Literature/evidence.tsv`
(pmid/doi + the sentence it supports), and an interpretation section ready for a Discussion.

---

## 10.1 Gene-set and pathway analysis — get the background right

| Analysis | Use | Requirements |
|---|---|---|
| ORA (over-representation) | simple list of DE genes | universe = **tested/expressed genes**; explicit up/down split; redundancy reduction |
| GSEA / fgsea / GSVA | full ranked list, no arbitrary cutoff | ranking metric stated (moderated t or shrunken log2FC); gene-set size limits; permutation scheme |
| WGCNA / module analysis | co-expression structure | soft-threshold reported; module–trait correlation with FDR; hub definition |
| ssGSEA / AUCell | per-sample pathway scores | score comparability across samples; no circular use as input to the same DE test |
| Single-cell pathway scoring | per-cell/per-pseudobulk scores | score cells, **test samples** (`06`) |

Common inflations to avoid:
1. **Wrong universe** (all genes instead of expressed genes) → systematically inflated enrichment.
2. **Testing thousands of redundant sets** without FDR → "significant pathway" is guaranteed.
3. **Gene length / expression-level bias** in ORA → use length-aware methods or state the bias.
4. **Tissue-specific background ignored** → brain-specific sets look "enriched" in brain data.
5. **Pooling up- and down-regulated genes** → directionality lost; report separately.
6. **Calling enrichment "activation"** → enrichment is about membership, not activity. For activity:
   TF activity inference (decoupleR/DoRothEA, SCENIC/AUCell regulons), kinase-substrate enrichment,
   or protein/phospho evidence. State the method and its confidence tier.
7. **Hand-picked gene sets** presented as unbiased discovery → label as hypothesis-driven.

Record for every enrichment result: method + version, database + version + access date, universe
size, FDR, set size, and the overlap genes in the supplementary table.

---

## 10.2 Databases and their versions (record, don't assume)

GO (release date) · KEGG (release; note licensing for redistribution) · Reactome (version) ·
MSigDB (version + collection: H/C2/C5/C7) · WikiPathways · InterPro/Pfam · STRING (version +
confidence threshold) · BioGRID/IntAct · HPA (protein evidence) · CellMarker/PanglaoDB (marker
provenance) · HCA/CELLxGENE (reference atlases) · HMDB/METLIN (metabolites) · UniProt (release).
Databases change; the same analysis in two years may give different answers. Store the version.

---

## 10.3 Per-finding interpretation protocol

For each important gene / protein / metabolite / pathway / population, produce a short block:

```
Finding:        <gene/population> is <higher/lower> in <condition> (log2FC=…, FDR=…, n=…)
Known function: <one sentence, cited PMID/DOI>
Disease role:   <established / suggested / not reported> + citation
Consistency:    <agrees with / contradicts> <specific studies — with PMIDs>
Upstream:       <regulators with evidence, or "none established">
Downstream:     <targets/effectors, or "not addressed">
Alternatives:   <≥1 alternative explanation for the observation>
Evidence grade: E1–E4 (per 15) + the verb you are therefore allowed to use
Next test:      <the experiment or dataset that would discriminate>
```

Rules:
- Every literature statement carries a **verifiable PMID or DOI that you actually retrieved**. If
  the retrieval failed, write "not verified" — never fill the gap from memory.
- Distinguish five registers explicitly: *established knowledge* · *this dataset* · *independent
  datasets* · *computational hypothesis* · *requires experimental verification*.
- Prioritise primary research, systematic reviews, and mechanistic studies over reviews of reviews.
- Actively search for **contradictory** evidence; a one-sided literature summary is a red flag to
  reviewers and a disservice to the science.
- Do not claim causality from observational transcriptomic/proteomic data.
- Do not upgrade a mouse-model mechanism to human relevance without saying so.

---

## 10.4 Immune and microenvironment analyses — extra caveats

- **Deconvolution** (CIBERSORTx, quanTIseq, xCell, EPIC, cell2location) yields *estimates* with
  method-specific bias; report the method, signature matrix, and a sensitivity run with a second
  method. Never present deconvolved fractions as measured abundances.
- **Immune "scores"** (ESTIMATE, ssGSEA) are relative within the analysed matrix — comparisons
  across studies are invalid unless re-computed jointly.
- **Bulk scRNA-derived signatures**: check that signature genes are not driven by tissue
  composition; a "T-cell signature" may be a purity readout.
- **Cell-type-specific expression from bulk** requires deconvolution assumptions; state them.

---

## 10.5 The Findings Ledger (the artefact that prevents over-claiming)

One row per claim, mirrored in the prose. Columns (`templates/Findings_Ledger.csv`):

`finding_id · claim (one sentence) · evidence_type · dataset(s) · statistic (effect + CI + P/FDR) ·
n (donors/samples) · grade E1–E4 · verb_used · contradicting_evidence · limitation ·
next_test · figure/table reference`

Rules: no claim appears in a figure, abstract, or chat summary without a row. When a claim's grade
is E1, the verb must be "associated". Auto-check before delivery: every headline claim has a row,
every row has a grade, and the verb matches the grade.

---

## 10.6 Interpretation checklist

- [ ] Enrichment universe = tested genes; up/down separated; method+DB versions recorded
- [ ] No "activation/inhibition" claim without activity-level evidence
- [ ] Every literature statement has a retrieved PMID/DOI; contradictions reported
- [ ] Five evidence registers separated in the text
- [ ] Deconvolution/signature caveats stated; two methods compared where used
- [ ] Each finding has an alternatives section and a discriminating next test
- [ ] Findings_Ledger.csv complete and consistent with the figures and the summary
