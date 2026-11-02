import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const workspaceDir = "C:/Users/khode/Documents/resume-keyword-extraction";
const buildDir = path.join(workspaceDir, ".pptx_build");
const outputDir = path.join(workspaceDir, "outputs");
const figureDir = path.join(outputDir, "figures");
const skillDir = "C:/Users/khode/.codex/plugins/cache/openai-primary-runtime/presentations/26.904.11930/skills/presentations";
const runtimePython = "C:/Users/khode/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
const finalPath = path.join(outputDir, "Resume_Keyword_Extraction_Mini_Project.pptx");

const { resolvePresentationFont } = await import(
  pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href,
);
const fontFamily = resolvePresentationFont();
const presentation = Presentation.create({ slideSize: { width: 1280, height: 720 } });
const navy = "#183B56";
const blue = "#1C4C70";
const teal = "#2A8C8C";
const dark = "#263744";
const muted = "#657783";
const white = "#FFFFFF";

function addText(slide, text, position, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: "none",
    line: { fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    typeface: fontFamily,
    fontSize: 22,
    color: dark,
    autoFit: "none",
    ...style,
  };
  return shape;
}

function addTitle(slide, title, subtitle = "") {
  addText(slide, title, { left: 64, top: 42, width: 1152, height: 62 }, {
    typeface: fontFamily, fontSize: 42, bold: true, color: navy,
  });
  if (subtitle) {
    addText(slide, subtitle, { left: 66, top: 111, width: 1120, height: 38 }, {
      typeface: fontFamily, fontSize: 19, color: muted,
    });
  }
}

async function addImage(slide, filename, alt, position) {
  const bytes = await fs.readFile(path.join(figureDir, filename));
  slide.images.add({ blob: new Uint8Array(bytes), contentType: "image/png", alt, fit: "contain", position });
}

// Slide 1: a minimal title and the project purpose.
{
  const slide = presentation.slides.add();
  slide.background.fill = white;
  addText(slide, "Resume Keyword\nExtraction Using NLP", { left: 78, top: 145, width: 1110, height: 170 }, {
    typeface: fontFamily, fontSize: 58, bold: true, color: navy,
  });
  addText(slide, "NLP Lab Mini Project", { left: 82, top: 340, width: 1000, height: 45 }, {
    typeface: fontFamily, fontSize: 28, color: teal,
  });
  addText(slide, "Extract useful terms from resumes and compare them with a job description.",
    { left: 82, top: 423, width: 1050, height: 82 }, {
      typeface: fontFamily, fontSize: 23, color: dark,
    });
  addText(slide, "962 source rows  |  166 unique resumes  |  25 categories",
    { left: 82, top: 590, width: 1050, height: 34 }, {
      typeface: fontFamily, fontSize: 18, color: muted,
    });
  slide.speakerNotes.textFrame.setText("Project context: data/UpdatedResumeDataSet.csv and the approved PROJECT_CONTEXT.md.");
}

// Slide 2: dataset scale and original category balance.
{
  const slide = presentation.slides.add();
  slide.background.fill = white;
  addTitle(slide, "Dataset and duplicate removal", "Exact repeated resume text was removed before corpus-level analysis.");
  await addImage(slide, "top_categories.png", "Bar chart showing the ten largest original resume categories", {
    left: 42, top: 166, width: 760, height: 440,
  });
  addText(slide, "962 source rows\n796 repeated copies removed\n166 unique resume texts\n\nLargest groups\nJava Developer  84\nTesting  70\nDevOps Engineer  55",
    { left: 842, top: 205, width: 370, height: 345 }, {
      typeface: fontFamily, fontSize: 23, color: dark,
    });
  addText(slide, "Category counts use the original CSV; later text analysis uses unique resumes.",
    { left: 845, top: 570, width: 345, height: 60 }, {
      typeface: fontFamily, fontSize: 16, color: muted,
    });
  slide.speakerNotes.textFrame.setText("Source: data/UpdatedResumeDataSet.csv; data/resumes_clean.csv; outputs/figures/top_categories.png.");
}

// Slide 3: the experiment-linked NLP sequence.
{
  const slide = presentation.slides.add();
  slide.background.fill = white;
  addTitle(slide, "NLP methodology", "Each stage reuses techniques from experiments 2 through 10.");
  addText(slide,
    "Experiments 2-3   Tokenize, clean, remove stopwords, and lemmatize\n\n" +
    "Experiments 4, 6, 7   POS-tag words and form noun-phrase candidates\n\n" +
    "Experiment 8   Add supporting entity labels with spaCy\n\n" +
    "Experiments 5, 9   Rank unigrams, bigrams, and trigrams with TF-IDF\n\n" +
    "Experiment 9   Compare resume and job text with cosine similarity\n\n" +
    "Experiment 10   Summarize categories, resume lengths, and common terms",
    { left: 78, top: 174, width: 1120, height: 480 }, {
      typeface: fontFamily, fontSize: 22, color: dark,
    });
  slide.speakerNotes.textFrame.setText("Methods are implemented in src/preprocess.py, linguistic.py, entities.py, keywords.py, matcher.py and eda.py.");
}

// Slide 4: observed results with separate source figures.
{
  const slide = presentation.slides.add();
  slide.background.fill = white;
  addTitle(slide, "Results", "The sample app found overlapping listed skills and returned a 57.6% cosine score.");
  await addImage(slide, "all_resumes_wordcloud.png", "Word cloud of frequent words across unique cleaned resumes", {
    left: 42, top: 172, width: 700, height: 376,
  });
  await addImage(slide, "resume_lengths.png", "Histogram of cleaned resume lengths", {
    left: 778, top: 208, width: 430, height: 285,
  });
  addText(slide, "Sample skills matched: Python, SQL, machine learning, AWS, Tableau\nTop TF-IDF examples: python sql (0.253); data analyst (0.253); scikit-learn (0.234)",
    { left: 72, top: 572, width: 1120, height: 82 }, {
      typeface: fontFamily, fontSize: 19, color: dark,
    });
  slide.speakerNotes.textFrame.setText("Sources: outputs/figures/all_resumes_wordcloud.png; outputs/figures/resume_lengths.png; app.py sample run. The similarity percentage is not a hiring probability.");
}

// Slide 5: findings and limits for a human reviewer.
{
  const slide = presentation.slides.add();
  slide.background.fill = white;
  addTitle(slide, "Conclusion and limitations");
  addText(slide, "Conclusion", { left: 74, top: 160, width: 490, height: 42 }, {
    typeface: fontFamily, fontSize: 27, bold: true, color: teal,
  });
  addText(slide,
    "The app turns unstructured resume text into ranked keywords and skill matches. It can support an initial review, while keeping the steps visible and explainable.",
    { left: 74, top: 216, width: 488, height: 220 }, {
      typeface: fontFamily, fontSize: 21, color: dark,
    });
  addText(slide, "Limitations", { left: 650, top: 160, width: 540, height: 42 }, {
    typeface: fontFamily, fontSize: 27, bold: true, color: teal,
  });
  addText(slide,
    "The skill list is limited. TF-IDF and cosine similarity depend on shared words, not meaning. spaCy may mislabel skills, and encoding artifacts remain in some resumes. Results need human review; no accuracy evaluation was performed.",
    { left: 650, top: 216, width: 550, height: 275 }, {
      typeface: fontFamily, fontSize: 21, color: dark,
    });
  addText(slide, "Similarity is a text comparison, not a candidate-fit probability.",
    { left: 74, top: 572, width: 1120, height: 40 }, {
      typeface: fontFamily, fontSize: 18, color: muted,
    });
  slide.speakerNotes.textFrame.setText("Limitations are based on the implemented rule-based skill list, corpus-derived TF-IDF and cosine similarity, general spaCy NER, and the absence of labeled evaluation data.");
}

await fs.mkdir(buildDir, { recursive: true });
await fs.mkdir(outputDir, { recursive: true });
const candidatePath = path.join(buildDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

// Render authoring previews to support slide-by-slide review.
for (let i = 0; i < presentation.slides.items.length; i++) {
  const slide = presentation.slides.items[i];
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(path.join(buildDir, `preview-${i + 1}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const { finalizePresentation } = await import(
  pathToFileURL(path.join(skillDir, "container_tools/artifact_tool_utils.mjs")).href,
);
const expectedSlideSizeEmu = `${1280 * 9525},${720 * 9525}`;
const requirements = {
  explicitTotalSlideCount: 5,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
};
const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath,
  pythonExecutable: runtimePython,
  integrityValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(skillDir, "container_tools/inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", expectedSlideSizeEmu],
  requiredNativeTableOwnerSlides: [],
  fontPolicy: { basis: "design", families: [fontFamily] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(buildDir, "validation.json"),
});
console.log(JSON.stringify({ finalPath, fontFamily, result }, null, 2));
