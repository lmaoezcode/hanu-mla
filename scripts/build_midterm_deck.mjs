import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";


const workspaceDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SKILL_DIR = "C:\\Users\\LamHoang\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.909.12148\\skills\\presentations";
const TMP_DIR = path.join(workspaceDir, "tmp", "presentation-build");
const FINAL_PPTX = path.join(workspaceDir, "output", "pptx", "MLA-2026-midterm-presentation.pptx");
const RUNTIME_PYTHON = "C:\\Users\\LamHoang\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const IMAGE_PATH = path.join(workspaceDir, "assets", "teacher-reading-review.png");

const { resolvePresentationFont, applyPresentationChartFont, finalizePresentation } = await import(
  pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href,
);

const FONT = resolvePresentationFont({ fontFamily: "Arial" });
const COLORS = {
  navy: "#183153",
  teal: "#2F7E86",
  coral: "#E97862",
  ink: "#17212B",
  gray: "#5D6873",
  line: "#D7DEE4",
  pale: "#EEF3F5",
  paper: "#F7F6F2",
  white: "#FFFFFF",
};


function addText(slide, text, position, options = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position,
    fill: options.fill ?? "none",
    line: options.line ?? { fill: "none", width: 0 },
    ...(options.borderRadius ? { borderRadius: options.borderRadius } : {}),
  });
  shape.text = text;
  shape.text.style = {
    typeface: FONT,
    fontSize: options.fontSize ?? 26,
    bold: options.bold ?? false,
    color: options.color ?? COLORS.ink,
    alignment: options.alignment ?? "left",
    autoFit: "none",
  };
  return shape;
}


function addSlideTitle(slide, title) {
  addText(slide, title, { left: 72, top: 40, width: 1136, height: 64 }, {
    fontSize: 43,
    bold: true,
    color: COLORS.navy,
  });
}


function setBackground(slide, color = COLORS.white) {
  slide.background.fill = color;
}


function addSourceNote(slide, script, sources = []) {
  const sourceText = sources.length
    ? `\n\nSources:\n${sources.map((item) => `- ${item}`).join("\n")}`
    : "";
  slide.speakerNotes.textFrame.setText(`${script}${sourceText}`);
}


await fs.mkdir(TMP_DIR, { recursive: true });
await fs.mkdir(path.dirname(FINAL_PPTX), { recursive: true });

const teacherImage = await fs.readFile(IMAGE_PATH);
const presentation = Presentation.create({
  slideSize: { width: 1280, height: 720 },
});


// Slide 1
{
  const slide = presentation.slides.add();
  setBackground(slide, COLORS.paper);

  addText(
    slide,
    "CEFR Based Sentence\nDifficulty Classification",
    { left: 72, top: 120, width: 650, height: 180 },
    { fontSize: 54, bold: true, color: COLORS.navy },
  );
  addText(
    slide,
    "Teacher support for reviewing English reading materials",
    { left: 76, top: 315, width: 570, height: 74 },
    { fontSize: 28, color: COLORS.gray },
  );
  addText(
    slide,
    "61FIT4MLA\nWeek 6 midterm project idea presentation",
    { left: 76, top: 565, width: 470, height: 78 },
    { fontSize: 21, color: COLORS.gray },
  );
  slide.images.add({
    blob: new Uint8Array(teacherImage),
    contentType: "image/png",
    alt: "Illustration of a teacher reviewing sentence difficulty in a reading passage",
    fit: "contain",
    position: { left: 590, top: 45, width: 690, height: 650 },
  });

  addSourceNote(
    slide,
    "Good morning. Our project is called CEFR Based Sentence Difficulty Classification for Teacher Support in Reading Material Review. We propose a support tool that predicts the CEFR difficulty of individual English sentences. The goal is to help a teacher review reading materials more consistently while keeping every final decision with the teacher.",
  );
}


// Slide 2
{
  const slide = presentation.slides.add();
  setBackground(slide);
  addSlideTitle(slide, "Problem and user");

  addText(
    slide,
    "A reading text can look suitable while a few sentences exceed the target level",
    { left: 72, top: 125, width: 1120, height: 92 },
    { fontSize: 34, bold: true, color: COLORS.ink },
  );

  const columns = [
    {
      x: 72,
      n: "01",
      title: "Teacher input",
      body: "A reading text selected for a known learner group",
    },
    {
      x: 448,
      n: "02",
      title: "Model output",
      body: "A predicted CEFR level and six probabilities for each sentence",
    },
    {
      x: 824,
      n: "03",
      title: "Teacher decision",
      body: "Keep, simplify, replace, or inspect the sentence in context",
    },
  ];
  for (const item of columns) {
    addText(slide, item.n, { left: item.x, top: 270, width: 82, height: 52 }, {
      fontSize: 34,
      bold: true,
      color: COLORS.coral,
    });
    addText(slide, item.title, { left: item.x, top: 330, width: 310, height: 48 }, {
      fontSize: 27,
      bold: true,
      color: COLORS.navy,
    });
    addText(slide, item.body, { left: item.x, top: 390, width: 315, height: 120 }, {
      fontSize: 24,
      color: COLORS.gray,
    });
  }

  addText(
    slide,
    "The model supports review. The teacher makes the final decision.",
    { left: 72, top: 590, width: 1120, height: 62 },
    { fontSize: 29, bold: true, color: COLORS.teal },
  );

  addSourceNote(
    slide,
    "At HANU, teachers often select or adapt reading texts for a specific class. A passage may look suitable overall but still contain a few sentences that are much harder than the target level. Checking every sentence manually takes time, and reviewers may judge the same sentence differently. Our tool accepts a teacher selected reading text, separates it into sentences, and returns a predicted CEFR level with six class probabilities for each sentence. The teacher can then keep, simplify, replace, or examine a sentence more closely. The tool supports material review. It does not grade learners or choose materials automatically.",
  );
}


// Slide 3
{
  const slide = presentation.slides.add();
  setBackground(slide, COLORS.paper);
  addSlideTitle(slide, "Data");

  addText(slide, "10,004", { left: 72, top: 135, width: 250, height: 78 }, {
    fontSize: 58,
    bold: true,
    color: COLORS.coral,
  });
  addText(slide, "independent English sentences", { left: 74, top: 215, width: 300, height: 62 }, {
    fontSize: 26,
    color: COLORS.ink,
  });
  addText(slide, "Length", { left: 74, top: 315, width: 120, height: 40 }, {
    fontSize: 23,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "5 to 34 words\nMedian 14\nMean about 14.8", { left: 74, top: 360, width: 260, height: 130 }, {
    fontSize: 22,
    color: COLORS.gray,
  });
  addText(slide, "Fields", { left: 74, top: 455, width: 130, height: 40 }, {
    fontSize: 23,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "text, level, source, category,\nformat, and license", { left: 74, top: 495, width: 300, height: 66 }, {
    fontSize: 20,
    color: COLORS.gray,
  });
  addText(slide, "Sources and licences", { left: 74, top: 565, width: 280, height: 40 }, {
    fontSize: 23,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "SCoRE and Wiki-Auto\nCC BY-NC-SA 4.0 and CC BY-SA 3.0", { left: 74, top: 607, width: 315, height: 72 }, {
    fontSize: 19,
    color: COLORS.gray,
  });

  const chart = slide.charts.add("bar", {
    position: { left: 410, top: 145, width: 790, height: 435 },
    categories: ["A1", "A2", "B1", "B2", "C1", "C2"],
    series: [{
      name: "Sentences",
      values: [124, 1271, 3305, 3330, 1744, 230],
      fill: COLORS.teal,
      points: [
        { idx: 0, fill: COLORS.coral },
        { idx: 5, fill: COLORS.coral },
      ],
    }],
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 45 },
    hasLegend: false,
    xAxis: {
      visible: true,
      textStyle: { typeface: FONT, fill: COLORS.gray, fontSize: 20, bold: true },
      line: { style: "solid", fill: COLORS.line, width: 1 },
      majorGridlines: null,
    },
    yAxis: {
      visible: true,
      min: 0,
      max: 3600,
      majorUnit: 1000,
      textStyle: { typeface: FONT, fill: COLORS.gray, fontSize: 16 },
      line: { style: "solid", fill: COLORS.line, width: 1 },
      majorGridlines: { style: "solid", fill: COLORS.line, width: 1 },
    },
    dataLabels: {
      showValue: true,
      position: "outEnd",
      textStyle: { typeface: FONT, fill: COLORS.ink, fontSize: 17, bold: true },
    },
    chartFill: COLORS.paper,
    chartLine: { fill: "none", width: 0 },
    plotAreaFill: COLORS.paper,
    plotAreaLine: { fill: "none", width: 0 },
  });
  applyPresentationChartFont(chart, { fontFamily: FONT });

  addText(
    slide,
    "A1 and C2 are rare, so class imbalance must shape training and evaluation.",
    { left: 410, top: 602, width: 790, height: 55 },
    { fontSize: 23, bold: true, color: COLORS.navy },
  );

  addSourceNote(
    slide,
    "We plan to use UniversalCEFR cefr sp en, matched to the official CEFR-SP files. It contains 10,004 independent English sentences from 5 to 34 words, with a median of 14 and a mean of about 14.8. The fields include text, CEFR level, source, category, format, and license. B1 and B2 contain most of the data, while A1 has 124 sentences and C2 has 230. The sources are SCoRE and Wiki-Auto. Hugging Face marks the data as CC BY-NC-SA 4.0. The original repository lists SCoRE under that license and Wiki-Auto under CC BY-SA 3.0. One real example is Is that your bike, labeled A1. CEFR-SP provides two expert labels. Their exact agreement is about 41.4 percent, although every disagreement is within one adjacent CEFR level. These labels therefore require cautious interpretation.",
    [
      "UniversalCEFR cefr_sp_en: https://huggingface.co/datasets/UniversalCEFR/cefr_sp_en",
      "CEFR-SP repository: https://github.com/yukiar/CEFR-SP/tree/main/CEFR-SP",
      "Arase et al. 2022: https://aclanthology.org/2022.emnlp-main.416/",
    ],
  );
}


// Slide 4
{
  const slide = presentation.slides.add();
  setBackground(slide);
  addSlideTitle(slide, "ML task alignment");

  addText(slide, "INPUT", { left: 78, top: 150, width: 180, height: 45 }, {
    fontSize: 20,
    bold: true,
    color: COLORS.coral,
  });
  addText(slide, '"Is that your bike?"', { left: 76, top: 200, width: 490, height: 80 }, {
    fontSize: 38,
    bold: true,
    color: COLORS.ink,
  });
  addText(slide, "One independent English sentence", { left: 78, top: 290, width: 440, height: 50 }, {
    fontSize: 23,
    color: COLORS.gray,
  });

  addText(slide, "TASK", { left: 650, top: 150, width: 180, height: 45 }, {
    fontSize: 20,
    bold: true,
    color: COLORS.coral,
  });
  addText(slide, "Six class classification", { left: 648, top: 200, width: 480, height: 70 }, {
    fontSize: 37,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "Output includes six probabilities and one predicted level", { left: 650, top: 285, width: 500, height: 72 }, {
    fontSize: 23,
    color: COLORS.gray,
  });

  addText(slide, "A1      A2      B1      B2      C1      C2", { left: 112, top: 425, width: 1055, height: 62 }, {
    fontSize: 37,
    bold: true,
    color: COLORS.teal,
    alignment: "center",
  });
  addText(slide, "CEFR labels are ordered", { left: 420, top: 500, width: 440, height: 48 }, {
    fontSize: 25,
    bold: true,
    color: COLORS.navy,
    alignment: "center",
  });
  addText(slide, "An A1 to A2 error is smaller than an A1 to C2 error", { left: 290, top: 555, width: 700, height: 55 }, {
    fontSize: 24,
    color: COLORS.gray,
    alignment: "center",
  });
  addText(slide, "Labels include expert judgment, so the teacher also sees uncertainty.", { left: 190, top: 632, width: 900, height: 45 }, {
    fontSize: 22,
    bold: true,
    color: COLORS.coral,
    alignment: "center",
  });

  addSourceNote(
    slide,
    "We formulate the project as six class sentence classification. The input is one independent English sentence. The output is a probability for A1, A2, B1, B2, C1, and C2, followed by the predicted level. For example, the input Is that your bike has the target label A1. CEFR levels have an order, so an A1 prediction of A2 is less serious than a prediction of C2. We still train a six class classifier, but our evaluation also measures the distance between the predicted and true levels. Showing probabilities is important because the labels are not perfectly objective and the teacher needs to see uncertainty.",
  );
}


// Slide 5
{
  const slide = presentation.slides.add();
  setBackground(slide, COLORS.paper);
  addSlideTitle(slide, "Model plan");

  addText(
    slide,
    "Baseline  Always predict B2, the most frequent training class",
    { left: 72, top: 120, width: 1136, height: 58 },
    { fontSize: 26, bold: true, color: COLORS.coral },
  );

  const table = slide.tables.add({
    rows: 3,
    columns: 3,
    left: 72,
    top: 205,
    width: 1136,
    height: 350,
    columnWidths: [260, 360, 516],
    values: [
      ["Model", "Main signal", "Reason and check"],
      [
        "TF-IDF and Logistic Regression",
        "Words and short phrases",
        "Strong lexical baseline. Inspect coefficients and performance by source for topic confounding.",
      ],
      [
        "BiLSTM with GloVe",
        "Word order and sequence",
        "Tests whether sequence adds value. Short sentences and limited data may cause overfitting.",
      ],
    ],
  });
  table.borders.assign({ style: "solid", fill: COLORS.line, width: 1 });
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 3 }).assign({
    fill: COLORS.navy,
    textStyle: { typeface: FONT, fontSize: 22, bold: true, color: COLORS.white },
    borders: { style: "solid", fill: COLORS.line, width: 1 },
    margins: { left: 12, right: 12, top: 10, bottom: 10 },
    anchor: "center",
  });
  table.cells.block({ row: 1, column: 0, rowCount: 2, columnCount: 3 }).assign({
    fill: COLORS.white,
    textStyle: { typeface: FONT, fontSize: 21, color: COLORS.ink },
    borders: { style: "solid", fill: COLORS.line, width: 1 },
    margins: { left: 14, right: 14, top: 12, bottom: 12 },
    anchor: "middle",
  });
  table.cells.block({ row: 2, column: 0, rowCount: 1, columnCount: 3 }).fill = COLORS.pale;

  addText(
    slide,
    "Both models use balanced class weights. BiLSTM also uses dropout and early stopping.",
    { left: 72, top: 595, width: 1136, height: 54 },
    { fontSize: 24, color: COLORS.navy, alignment: "center" },
  );

  addSourceNote(
    slide,
    "Our baseline always predicts B2, the most frequent class in the training data. This is the simple method that both trained models should beat. Model one uses word unigram and bigram TF-IDF features with multinomial Logistic Regression and balanced class weights. We expect vocabulary and short phrases to provide strong CEFR signals. We will inspect its top coefficients and compare performance by source because TF-IDF could learn topic or dataset source instead of difficulty. Model two is a BiLSTM with 100 dimensional GloVe embeddings, dropout, class weighted cross entropy, and early stopping. It tests whether word order and sequential structure add useful information. The sentences are short and the dataset has about 10,000 examples, so the BiLSTM may produce only a small gain or may overfit. That limitation is part of the comparison.",
  );
}


// Slide 6
{
  const slide = presentation.slides.add();
  setBackground(slide);
  addSlideTitle(slide, "Evaluation plan");

  const splits = [
    { x: 72, value: "7,178", label: "Train", note: "7,177 after one duplicate" },
    { x: 435, value: "1,366", label: "Validation", note: "Model selection" },
    { x: 798, value: "1,460", label: "Test", note: "Used once at the end" },
  ];
  for (const item of splits) {
    addText(slide, item.value, { left: item.x, top: 135, width: 300, height: 70 }, {
      fontSize: 51,
      bold: true,
      color: COLORS.coral,
      alignment: "center",
    });
    addText(slide, item.label, { left: item.x, top: 205, width: 300, height: 44 }, {
      fontSize: 26,
      bold: true,
      color: COLORS.navy,
      alignment: "center",
    });
    addText(slide, item.note, { left: item.x, top: 250, width: 300, height: 48 }, {
      fontSize: 19,
      color: COLORS.gray,
      alignment: "center",
    });
  }

  addText(slide, "Split discipline", { left: 72, top: 340, width: 300, height: 45 }, {
    fontSize: 25,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "Official CEFR-SP split separates highly similar sentences. Fit preprocessing on train only.", { left: 72, top: 390, width: 520, height: 105 }, {
    fontSize: 23,
    color: COLORS.gray,
  });

  addText(slide, "Main metrics", { left: 650, top: 340, width: 300, height: 45 }, {
    fontSize: 25,
    bold: true,
    color: COLORS.navy,
  });
  addText(slide, "Macro-F1 for class imbalance\nQuadratic weighted kappa for ordered errors", { left: 650, top: 390, width: 500, height: 105 }, {
    fontSize: 23,
    color: COLORS.gray,
  });

  addText(slide, "Report accuracy, confusion matrix, and per-class precision, recall, F1, and support.", { left: 72, top: 545, width: 1100, height: 55 }, {
    fontSize: 22,
    color: COLORS.ink,
    alignment: "center",
  });
  addText(slide, "95 percent confidence intervals from 1,000 stratified bootstrap samples", { left: 150, top: 615, width: 980, height: 45 }, {
    fontSize: 22,
    bold: true,
    color: COLORS.teal,
    alignment: "center",
  });

  addSourceNote(
    slide,
    "We will use the official CEFR-SP split: 7,178 sentences for training, 1,366 for validation, and 1,460 for testing. The split was designed to keep highly similar sentences from appearing in both training and validation or test data. We will remove one exact duplicate inside the training set, leaving 7,177 unique training sentences. We will fit the tokenizer, vocabulary, and TF-IDF representation on training data only. The validation set will guide hyperparameters and early stopping, and the test set will be used once after the model choices are fixed. Our primary metric is macro-F1 because it gives equal importance to every class. We will also report quadratic weighted kappa because CEFR levels are ordered and distant errors matter more. The report will include accuracy, a confusion matrix, and per-class precision, recall, F1, and support. We will estimate 95 percent confidence intervals with 1,000 stratified bootstrap samples. A1 results need cautious interpretation because the test set contains only 37 A1 sentences.",
    [
      "CEFR-SP repository and official split: https://github.com/yukiar/CEFR-SP/tree/main/CEFR-SP",
      "Arase et al. 2022: https://aclanthology.org/2022.emnlp-main.416/",
    ],
  );
}


// Slide 7
{
  const slide = presentation.slides.add();
  setBackground(slide, COLORS.paper);
  addSlideTitle(slide, "Risks and responsible use");

  const leftItems = [
    ["Label ambiguity", "Show probabilities and report annotator disagreement"],
    ["Class imbalance", "Use class weights, macro-F1, and class support"],
    ["Topic confounding", "Inspect coefficients and results by source"],
  ];
  const rightItems = [
    ["Domain shift", "Review about 30 representative HANU sentences"],
    ["Sentence scope", "Avoid claims about the CEFR level of a full passage"],
    ["Learner variability", "Interpret every prediction in classroom context"],
  ];

  function addRiskColumn(items, x) {
    let y = 145;
    for (const [label, body] of items) {
      addText(slide, label, { left: x, top: y, width: 480, height: 42 }, {
        fontSize: 25,
        bold: true,
        color: COLORS.navy,
      });
      addText(slide, body, { left: x, top: y + 45, width: 480, height: 68 }, {
        fontSize: 22,
        color: COLORS.gray,
      });
      y += 135;
    }
  }

  addRiskColumn(leftItems, 72);
  addRiskColumn(rightItems, 690);

  addText(
    slide,
    "Predictions guide attention. The teacher reviews the sentence and makes the decision.",
    { left: 105, top: 590, width: 1070, height: 70 },
    { fontSize: 29, bold: true, color: COLORS.teal, alignment: "center" },
  );

  addSourceNote(
    slide,
    "The main risks are label ambiguity, class imbalance, topic confounding, and a mismatch between the public data and HANU reading materials. We address imbalance with class weighting and macro-F1. We check topic confounding through Logistic Regression coefficients and results by source. Before the final project, we will also review about 30 representative sentences from HANU materials as a qualitative local check. These sentences will not be used for training. The model evaluates sentences, not complete passages, and the same sentence may feel different to learners with different background knowledge. For these reasons, predictions remain suggestions with probabilities. The teacher reviews the sentence in context and makes the final decision. Thank you. We are ready for your questions.",
  );
}


for (let index = 0; index < presentation.slides.length; index += 1) {
  const slide = presentation.slides.getItemAt(index);
  const preview = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(
    path.join(TMP_DIR, `draft-slide-${index + 1}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const requirements = {
  explicitTotalSlideCount: 7,
  requiredNativeTableOwnerSlides: [5],
  requiredNativeChartOwnerSlides: [3],
  requiredEmbeddedWorkbookChartOwnerSlides: [],
  materializeLiteralChartWorkbooks: true,
};
const fontPolicy = { basis: "design", families: [FONT] };
const expectedSlideSizeEmu = "12192000,6858000";
const stagingDir = path.join(workspaceDir, ".codex-finalizer-midterm");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const result = await finalizePresentation({
  ...requirements,
  workspaceDir,
  candidatePath,
  finalPath: FINAL_PPTX,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", expectedSlideSizeEmu,
    "--validate-bullet-geometry",
    "--validate-heading-fit",
    "--require-native-table-slide", "5",
  ],
  requiredNativeTableOwnerSlides: requirements.requiredNativeTableOwnerSlides,
  fontPolicy,
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "MLA-2026-midterm-presentation.validation.json"),
});

console.log(JSON.stringify({ finalPath: FINAL_PPTX, font: FONT, result }, null, 2));
