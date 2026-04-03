const fs = require('fs');
const path = require('path');
const mergeRoot = process.argv[2];
const selectedPath = process.argv[3];
const selected = JSON.parse(fs.readFileSync(selectedPath, 'utf8'));
let totals = {
  request_count:0, successful_request_count:0, failed_request_count:0, retry_count:0,
  text_request_count:0, multimodal_request_count:0, requests_with_usage:0,
  prompt_tokens:0, completion_tokens:0, total_tokens:0, cached_tokens:0,
  reasoning_tokens:0, total_request_seconds:0
};
let decisionTotals = {pass:0, review:0, reject:0};
let rewriteTotals = {};
let totalProcessed = 0;
let totalRequested = 0;
let startedAt = null;
let finishedAt = null;
const mergedBatches = [];
for (const item of selected) {
  const sumPath = path.join(item.source, 'summary.json');
  const d = JSON.parse(fs.readFileSync(sumPath, 'utf8'));
  const ds = d.datasets[0];
  totalProcessed += ds.processed_samples || 0;
  totalRequested += ds.requested_samples || 0;
  for (const [k,v] of Object.entries(ds.decision_counts || {})) decisionTotals[k] = (decisionTotals[k]||0)+v;
  for (const [k,v] of Object.entries(ds.rewrite_strategy_counts || {})) rewriteTotals[k] = (rewriteTotals[k]||0)+v;
  for (const [k,v] of Object.entries(ds.llm_usage || {})) if (typeof v === 'number' && Object.prototype.hasOwnProperty.call(totals, k)) totals[k] += v;
  if (!startedAt || new Date(d.started_at) < new Date(startedAt)) startedAt = d.started_at;
  if (!finishedAt || new Date(d.finished_at) > new Date(finishedAt)) finishedAt = d.finished_at;
  mergedBatches.push({range:item.range, source:item.source, pipeline_run_id:d.pipeline_run_id, summary_path:path.join(item.source,'summary.json')});
}
const datasetSummary = {
  dataset_key: 'physreason',
  dataset_name: 'PhysReason',
  subject: '物理',
  source_status: 'available',
  detail: 'Merged from main 0:300 batches with rerun replacement for 0180:0260 after historical 502/fallback risk.',
  requested_samples: totalRequested,
  processed_samples: totalProcessed,
  decision_counts: decisionTotals,
  rewrite_strategy_counts: rewriteTotals,
  records_dir: 'datasets/physreason/records',
  sample_concurrency: 1,
  started_at: startedAt,
  finished_at: finishedAt,
  elapsed_seconds: (new Date(finishedAt)-new Date(startedAt))/1000,
  llm_usage: {...totals, last_error: null},
  merged_batches: mergedBatches
};
const topSummary = {
  pipeline_run_id: 'run_merged_physreason_0000_0300',
  created_at: new Date().toISOString(),
  datasets: [{dataset_key:'physreason', dataset_name:'PhysReason', summary_path:'datasets/physreason/summary.json'}],
  sample_concurrency: 1,
  started_at: startedAt,
  finished_at: finishedAt,
  elapsed_seconds: datasetSummary.elapsed_seconds,
  llm_usage: {...totals, last_error: null}
};
fs.mkdirSync(path.join(mergeRoot, 'datasets/physreason'), {recursive:true});
fs.writeFileSync(path.join(mergeRoot, 'datasets/physreason/summary.json'), JSON.stringify(datasetSummary, null, 2));
fs.writeFileSync(path.join(mergeRoot, 'summary.json'), JSON.stringify(topSummary, null, 2));
