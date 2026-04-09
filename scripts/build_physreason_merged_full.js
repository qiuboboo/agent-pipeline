#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const mergeRoot = process.argv[2];
const selectedPath = process.argv[3];
if (!mergeRoot || !selectedPath) {
  console.error('Usage: build_physreason_merged_full.js <mergeRoot> <selected_batches.json>');
  process.exit(1);
}
const selected = JSON.parse(fs.readFileSync(selectedPath, 'utf8'));
const datasetRoot = path.join(mergeRoot, 'datasets', 'physreason');
const samplesDst = path.join(datasetRoot, 'samples');
const imagesDst = path.join(datasetRoot, 'artifacts', 'images');
const cropsDst = path.join(datasetRoot, 'artifacts', 'crops');
const recordsDst = path.join(datasetRoot, 'records');
for (const p of [samplesDst, imagesDst, cropsDst, recordsDst]) fs.mkdirSync(p, { recursive: true });

const recordBuffers = new Map();
for (const item of selected) {
  const src = item.source;
  const samplesSrc = path.join(src, 'datasets', 'physreason', 'samples');
  const imagesSrc = path.join(src, 'datasets', 'physreason', 'artifacts', 'images');
  const cropsSrc = path.join(src, 'datasets', 'physreason', 'artifacts', 'crops');
  const recordsSrc = path.join(src, 'datasets', 'physreason', 'records');

  if (fs.existsSync(samplesSrc)) {
    for (const name of fs.readdirSync(samplesSrc)) {
      fs.copyFileSync(path.join(samplesSrc, name), path.join(samplesDst, name));
    }
  }
  if (fs.existsSync(imagesSrc)) {
    for (const name of fs.readdirSync(imagesSrc)) {
      fs.copyFileSync(path.join(imagesSrc, name), path.join(imagesDst, name));
    }
  }
  if (fs.existsSync(cropsSrc)) {
    for (const name of fs.readdirSync(cropsSrc)) {
      fs.copyFileSync(path.join(cropsSrc, name), path.join(cropsDst, name));
    }
  }
  if (fs.existsSync(recordsSrc)) {
    for (const name of fs.readdirSync(recordsSrc)) {
      const full = path.join(recordsSrc, name);
      if (!fs.statSync(full).isFile()) continue;
      const content = fs.readFileSync(full, 'utf8');
      if (!recordBuffers.has(name)) recordBuffers.set(name, []);
      if (content.trim()) recordBuffers.get(name).push(content.trimEnd());
    }
  }
}
for (const [name, chunks] of recordBuffers.entries()) {
  fs.writeFileSync(path.join(recordsDst, name), chunks.join('\n') + '\n');
}

const manifest = {
  created_at: new Date().toISOString(),
  dataset: 'physreason',
  selected_batch_count: selected.length,
  selected_batches: selected,
  copied: {
    sample_files: fs.readdirSync(samplesDst).length,
    image_files: fs.existsSync(imagesDst) ? fs.readdirSync(imagesDst).length : 0,
    crop_files: fs.existsSync(cropsDst) ? fs.readdirSync(cropsDst).length : 0,
    record_files: fs.existsSync(recordsDst) ? fs.readdirSync(recordsDst).length : 0,
  }
};
fs.writeFileSync(path.join(mergeRoot, 'records', 'FULL_MERGE_MANIFEST.json'), JSON.stringify(manifest, null, 2));
console.log(JSON.stringify(manifest, null, 2));
