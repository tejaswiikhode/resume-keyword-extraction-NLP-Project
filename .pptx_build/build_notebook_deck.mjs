import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const root = process.cwd();
const skillDir = "C:/Users/khode/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations";
const buildDir = path.join(root, ".pptx_build");
const outputDir = path.join(root, "outputs");
const finalPath = path.join(outputDir, "Resume_Keyword_Extraction_Presentation_10_Slides.pptx");
const { resolvePresentationFont, finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href
);
await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(path.join(buildDir, "previews"), { recursive: true });
await fs.mkdir(outputDir, { recursive: true });
const font = resolvePresentationFont({ fontFamily: "Aptos" });

const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const C = { navy: "#17324D", teal: "#147D83", ink: "#263746", muted: "#5D6B75", paper: "#FBFCFA", pale: "#EAF2F4", white: "#FFFFFF" };

function text(slide, value, x, y, w, h, size = 28, color = C.ink, bold = false) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = value;
  shape.text.style = {
    typeface: font,
    fontSize: size,
    color,
    bold,
    autoFit: "shrinkText",
    verticalAlignment: "middle",
  };
  return shape;
}

function makeSlide(title, note, subtitle = "") {
  const slide = presentation.slides.add();
  slide.background.fill = C.paper;
  text(slide, title, 72, 42, 1136, 65, 42, C.navy, true);
  if (subtitle) text(slide, subtitle, 74, 108, 1120, 38, 22, C.teal, true);
  text(slide, String(presentation.slides.items.length).padStart(2, "0"), 1160, 665, 48, 28, 15, C.muted, true);
  slide.speakerNotes.textFrame.setText(note);
  return slide;
}

function addBullets(slide, items, x = 92, y = 180, w = 1080, size = 27, gap = 66) {
  items.forEach((item, index) => {
    text(slide, "•", x, y + index * gap + 2, 32, 42, size, C.teal, true);
    text(slide, item, x + 40, y + index * gap, w - 40, 54, size, C.ink, false);
  });
}

async function addImage(slide, filename, alt, position) {
  const bytes = new Uint8Array(await fs.readFile(path.join(outputDir, "figures", filename)));
  slide.images.add({ blob: bytes, contentType: "image/png", alt, fit: "contain", position });
}

// 1. Cover
{
  const slide = presentation.slides.add();
  slide.background.fill = C.paper;
  text(slide, "Resume Keyword\nExtraction using NLP", 82, 122, 1080, 190, 62, C.navy, true);
  text(slide, "Mini Project Presentation", 86, 342, 990, 56, 32, C.teal, true);
  text(slide, "An explainable pipeline for resume keywords and job-text matching", 88, 418, 1060, 68, 25, C.ink, false);
  text(slide, "NLP Lab  |  Dataset: 962 resumes across 25 categories", 88, 555, 1060, 42, 20, C.muted, false);
  text(slide, "01", 1160, 665, 48, 28, 15, C.muted, true);
  slide.speakerNotes.textFrame.setText("Source: project.ipynb and data/UpdatedResumeDataSet.csv. This presentation describes the implemented notebook and its recorded outputs.");
}

// 2. Problem and objective
{
  const slide = makeSlide("Problem and project objective", "Problem statement from experiment 1; project objective implemented in project.ipynb.");
  addBullets(slide, [
    "Manual resume screening takes time when many applications arrive.",
    "Relevant skills and qualifications may be missed in free-form text.",
    "Extract and rank candidate keywords to make review more structured.",
    "Compare a resume with a job description, while leaving decisions to a person.",
  ], 92, 168, 1080, 26, 88);
}

// 3. Dataset and duplicate removal
{
  const slide = makeSlide("Dataset and duplicate handling", "Notebook cells 4–7. Source: data/UpdatedResumeDataSet.csv.", "The category chart uses all source rows; corpus analysis uses unique resume texts.");
  text(slide, "962", 105, 198, 300, 96, 64, C.navy, true);
  text(slide, "source rows", 108, 292, 300, 44, 22, C.muted, false);
  text(slide, "25", 489, 198, 250, 96, 64, C.teal, true);
  text(slide, "categories", 493, 292, 250, 44, 22, C.muted, false);
  text(slide, "796", 825, 198, 300, 96, 64, C.navy, true);
  text(slide, "exact duplicate rows removed", 829, 292, 365, 44, 22, C.muted, false);
  text(slide, "166 unique resumes remain. Category and Resume columns have no missing values.", 104, 405, 1080, 86, 29, C.ink, false);
  text(slide, "Exact-text deduplication keeps the first copy for each resume.", 104, 530, 1060, 55, 22, C.muted, false);
}

// 4. Pipeline overview
{
  const slide = makeSlide("Notebook workflow", "Method sequence and experiment links documented in project.ipynb.");
  addBullets(slide, [
    "Inspect, deduplicate, and clean text — experiments 1, 2, 10",
    "Remove stopwords and lemmatize — experiment 3",
    "Tag parts of speech and chunk noun phrases — experiments 4, 6, 7",
    "Find named entities and listed skills — experiment 8",
    "Rank terms, compare job text, and explore charts — experiments 5, 9, 10",
  ], 90, 152, 1100, 25, 88);
}

// 5. Linguistic preprocessing
{
  const slide = makeSlide("Text normalization and phrase candidates", "Experiments 2, 3, 4, 6, and 7.");
  addBullets(slide, [
    "Normalize whitespace and selected encoding artifacts; preserve technical forms such as C++, C#, and .NET.",
    "Remove English stopwords, then lemmatize tokens for downstream analysis.",
    "Use NLTK POS tags to demonstrate morphology and simple adjective–noun phrase chunks.",
    "Phrase chunks are candidates; fragmented resume lists can produce awkward results.",
  ], 88, 157, 1105, 25, 90);
}

// 6. NER and skill lexicon
{
  const slide = makeSlide("Entity and skill extraction", "Experiment 8. spaCy NER is supplemented by the notebook's editable common-skills list.");
  addBullets(slide, [
    "spaCy identifies general entities such as people, organizations, places, and dates.",
    "A transparent skill list checks terms such as Python, SQL, machine learning, AWS, and Tableau.",
    "In the sample resume, spaCy sometimes labels technical terms as PERSON, GPE, or ORG.",
    "NER results are supporting clues; the skill list is more direct for listed technologies.",
  ], 88, 157, 1105, 25, 90);
}

// 7. Keywords and matching
{
  const slide = makeSlide("TF-IDF keywords and job matching", "Experiments 5 and 9.");
  addBullets(slide, [
    "TF-IDF ranks unigrams, bigrams, and trigrams across 166 unique resumes.",
    "Top terms are combined with noun-phrase candidates and skills found in the resume.",
    "Cosine similarity compares the resume and job description; listed skills are split into matched and missing.",
  ], 88, 151, 1090, 24, 83);
  text(slide, "Recorded demo: 29.5% cosine similarity; 6 of 7 listed job skills matched.", 100, 438, 1075, 58, 25, C.teal, true);
  text(slide, "The percentage depends on the wording and the two-document TF-IDF space. It is not a hiring score.", 100, 512, 1075, 70, 21, C.muted, false);
}

// 8. Category and length charts
{
  const slide = makeSlide("Dataset results and text lengths", "Experiment 10. The category bars count original rows; the histogram describes 166 unique resumes.");
  await addImage(slide, "top_categories.png", "Bar chart of the ten most frequent resume categories", { left: 78, top: 164, width: 650, height: 420 });
  await addImage(slide, "resume_lengths.png", "Histogram of token counts in unique resumes", { left: 735, top: 164, width: 465, height: 420 });
  text(slide, "Most common: Java Developer (84), Testing (70), DevOps Engineer (55).", 97, 592, 1080, 38, 20, C.ink, false);
}

// 9. Word clouds
{
  const slide = makeSlide("Word cloud exploration", "Experiment 10. These images summarize word frequency after stopword removal.");
  await addImage(slide, "all_resumes_wordcloud.png", "Word cloud for all unique resumes", { left: 74, top: 152, width: 570, height: 250 });
  await addImage(slide, "java_developer_wordcloud.png", "Word cloud for Java Developer resumes", { left: 648, top: 152, width: 560, height: 250 });
  await addImage(slide, "testing_wordcloud.png", "Word cloud for Testing resumes", { left: 74, top: 412, width: 570, height: 230 });
  await addImage(slide, "devops_engineer_wordcloud.png", "Word cloud for DevOps Engineer resumes", { left: 648, top: 412, width: 560, height: 230 });
}

// 10. Limits and conclusion
{
  const slide = makeSlide("Conclusion and limitations", "Summary based on the implemented notebook and sample outputs.");
  addBullets(slide, [
    "The notebook joins preprocessing, linguistic analysis, TF-IDF, similarity, and visual summaries.",
    "The editable skill list is incomplete; POS chunks may be noisy; general spaCy NER can mislabel technologies.",
    "Cosine similarity reflects shared wording, not experience quality or candidate suitability.",
    "Use extracted terms to support human review, never as the sole hiring decision.",
  ], 86, 153, 1110, 24, 91);
}

const stagingDir = path.join(buildDir, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate_notebook_10slides.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

// Save a PNG of every slide so the layout can be reviewed before delivery.
for (let index = 0; index < presentation.slides.items.length; index++) {
  const slide = presentation.slides.items[index];
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(buildDir, "previews", `notebook-slide-${index + 1}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const finalized = await finalizePresentation({
  explicitTotalSlideCount: 10,
  requiredNativeChartOwnerSlides: [],
  requiredNativeTableOwnerSlides: [],
  workspaceDir: root,
  candidatePath,
  finalPath,
  pythonExecutable: "C:/Users/khode/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe",
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-bullet-geometry", "--validate-heading-fit"],
  fontPolicy: { basis: "design", families: [font] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "notebook_10slides.validation.json"),
});
console.log(JSON.stringify({ finalPath, slides: presentation.slides.items.length, font, finalized }, null, 2));
