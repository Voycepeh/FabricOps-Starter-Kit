export const VIDEO_FPS = 30;

export const narrationFrame = (seconds: number) => Math.round(seconds * VIDEO_FPS);

type PhraseCue = {
  phrase: string;
  atSeconds: number;
};

const sceneCue = (
  scene: string,
  audioStartSeconds: number,
  audioEndSeconds: number,
  transitionSeconds: number,
  phrases: PhraseCue[],
) => ({
  scene,
  audioStartSeconds,
  audioEndSeconds,
  startFrame: narrationFrame(audioStartSeconds),
  endFrame: narrationFrame(audioEndSeconds),
  keySpokenPhrase: phrases[0].phrase,
  phraseTimestampSeconds: phrases[0].atSeconds,
  animationTriggerFrame: narrationFrame(phrases[0].atSeconds),
  transitionFrame: narrationFrame(transitionSeconds),
  keyPhrases: phrases.map(({phrase, atSeconds}) => ({
    phrase,
    atSeconds,
    triggerFrame: narrationFrame(atSeconds),
  })),
});

export const NARRATION_DURATION_SECONDS = 475.3;
export const FINAL_FADE_END_SECONDS = 476.3;
export const NARRATION_END_FRAME = narrationFrame(NARRATION_DURATION_SECONDS);
export const FINAL_VIDEO_FRAME = narrationFrame(FINAL_FADE_END_SECONDS);

export const NARRATION_CUE_SHEET = {
  opening: sceneCue('Opening', 0, 18.2, 18.2, [
    {phrase: 'Microsoft Fabric gives us a powerful all-in-one analytics platform.', atSeconds: 0},
    {phrase: 'So where do we start?', atSeconds: 15.2},
  ]),
  fabricOps: sceneCue('FabricOps solution', 18.2, 54, 54, [
    {phrase: 'FabricOps, short for Fabric Operations.', atSeconds: 18.2},
    {phrase: 'Why FabricOps?', atSeconds: 39.3},
    {phrase: 'How does it actually work?', atSeconds: 50.4},
  ]),
  notebooks: sceneCue('Notebook journey', 54, 115, 115, [
    {phrase: 'We created multiple functions and widgets.', atSeconds: 54},
    {phrase: 'Download our Python package.', atSeconds: 60.5},
    {phrase: 'Wire functions into the notebooks.', atSeconds: 71},
    {phrase: '01 Governance and 02 Engineering.', atSeconds: 79},
    {phrase: 'At the center is the Data Contract.', atSeconds: 86},
  ]),
  lifecycle: sceneCue('Seven-step lifecycle', 115, 175, 175, [
    {phrase: 'FabricOps follows a simple seven-step workflow.', atSeconds: 115},
    {phrase: 'One: define the Data Agreement.', atSeconds: 120},
    {phrase: 'Two: build ETL, profile, and catalogue.', atSeconds: 123},
    {phrase: 'Three: enrich and freeze the Data Contract.', atSeconds: 128},
    {phrase: 'Four: rerun ETL with the Data Contract.', atSeconds: 137},
    {phrase: 'Five: activate and promote.', atSeconds: 154},
    {phrase: 'Six: run the Production pipeline.', atSeconds: 169},
  ]),
  consumption: sceneCue('Consumption', 175, 190.217, 190.217, [
    {phrase: 'Seven: approved Production data is ready to be consumed.', atSeconds: 176.25},
    {phrase: 'Approved and available.', atSeconds: 177.64},
    {phrase: 'Production database.', atSeconds: 179.7},
    {phrase: 'Dashboards.', atSeconds: 183.4},
    {phrase: 'Data Agents.', atSeconds: 184.58},
    {phrase: 'Applications.', atSeconds: 185.43},
    {phrase: 'Machine learning models.', atSeconds: 187.45},
  ]),
  dataEngineers: sceneCue('Data Engineers', 190.217, 222.3, 222.3, [
    {phrase: 'For data engineers, how much time do we spend rewriting boilerplate?', atSeconds: 190.58},
    {phrase: 'Connecting to data stores.', atSeconds: 196},
    {phrase: 'Resolving paths.', atSeconds: 199.12},
    {phrase: 'Profiling and EDA.', atSeconds: 200.58},
    {phrase: 'Data quality checks.', atSeconds: 204.08},
    {phrase: 'AI helps us write code faster.', atSeconds: 205.58},
    {phrase: 'Faster does not always mean consistent.', atSeconds: 211.62},
    {phrase: 'Different implementations.', atSeconds: 216.95},
  ]),
  repeatablePipeline: sceneCue('Repeatable Pipeline', 222.3, 252.24, 252.24, [
    {phrase: 'A standard template for data pipelines.', atSeconds: 222.3},
    {phrase: 'orchestrate_read.', atSeconds: 233.12},
    {phrase: 'orchestrate_write.', atSeconds: 234.49},
    {phrase: 'Project-specific data transformation.', atSeconds: 239.79},
    {phrase: 'Full refresh.', atSeconds: 244.44},
    {phrase: 'Incremental load.', atSeconds: 245.49},
    {phrase: 'Slowly changing dimensions.', atSeconds: 247.01},
  ]),
  sensitiveData: sceneCue('Sensitive Data', 252.24, 288.56, 288.56, [
    {phrase: 'For the data governance team.', atSeconds: 252.56},
    {phrase: 'Define which columns are sensitive.', atSeconds: 260.34},
    {phrase: 'Masked.', atSeconds: 267.17},
    {phrase: 'Hashed.', atSeconds: 268.88},
    {phrase: 'Tokenized.', atSeconds: 270.41},
    {phrase: 'Requirements translated into a Data Contract.', atSeconds: 274.93},
    {phrase: 'Entirely masked or dropped.', atSeconds: 282.79},
  ]),
  businessRules: sceneCue('Business Rules to DQ', 288.56, 334.12, 334.12, [
    {phrase: 'For business users.', atSeconds: 288.56},
    {phrase: 'Describe requirements in plain English.', atSeconds: 301.14},
    {phrase: 'Every completed order must have a delivery date.', atSeconds: 303.33},
    {phrase: 'AI translates requirements into a data quality rule.', atSeconds: 311.98},
    {phrase: 'Review and approve.', atSeconds: 318.35},
    {phrase: 'Engineers review complex rules.', atSeconds: 328.66},
  ]),
  bigPicture: sceneCue('The Big Picture', 334.12, 402.25, 402.25, [
    {phrase: 'Requirements translate into code enforced in the pipeline.', atSeconds: 335.32},
    {phrase: 'orchestrate_read.', atSeconds: 345.49},
    {phrase: 'PySpark transformation.', atSeconds: 351.45},
    {phrase: 'orchestrate_write.', atSeconds: 357.38},
    {phrase: 'Check the Data Contract.', atSeconds: 363.95},
    {phrase: 'Sensitive-data treatment.', atSeconds: 366.19},
    {phrase: 'Data quality.', atSeconds: 368.24},
    {phrase: 'Customer identifiers are masked.', atSeconds: 370.83},
    {phrase: 'One row failed.', atSeconds: 378.55},
    {phrase: 'Governance as code in action.', atSeconds: 386.52},
    {phrase: 'Business and governance requirements become executable rules.', atSeconds: 389.34},
  ]),
  promotion: sceneCue('Promotion', 402.25, 426.34, 426.34, [
    {phrase: 'Clone and promote the pipelines.', atSeconds: 405.64},
    {phrase: 'Through the deployment pipeline.', atSeconds: 415.31},
    {phrase: 'Environment configuration.', atSeconds: 416.71},
    {phrase: 'The pipeline itself.', atSeconds: 419.34},
    {phrase: 'The Data Contracts.', atSeconds: 421.58},
    {phrase: 'From Development.', atSeconds: 422.64},
    {phrase: 'To Production.', atSeconds: 424.4},
  ]),
  closing: sceneCue('Closing', 426.34, NARRATION_DURATION_SECONDS, FINAL_FADE_END_SECONDS, [
    {phrase: 'From Development to Production.', atSeconds: 426.34},
    {phrase: 'Plug-and-play data pipelines.', atSeconds: 436.77},
    {phrase: 'Governance as code.', atSeconds: 438.81},
    {phrase: 'Teams collaborate and build reliable pipelines.', atSeconds: 441.64},
    {phrase: 'High-quality trusted data matters more than ever.', atSeconds: 448.32},
    {phrase: 'Data Agents, ML, or applications.', atSeconds: 457.98},
    {phrase: 'Continue reading our documentation.', atSeconds: 466.44},
    {phrase: 'Follow our hands-on guided demo.', atSeconds: 472.61},
  ]),
} as const;
