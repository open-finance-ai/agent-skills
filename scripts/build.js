#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const archiver = require('archiver');

const SKILLS_DIR = path.join(__dirname, '..', 'skills');
const DIST_DIR = path.join(__dirname, '..', 'dist');

function buildSkill(skillName) {
  return new Promise((resolve, reject) => {
    const skillPath = path.join(SKILLS_DIR, skillName);
    const outputPath = path.join(DIST_DIR, `${skillName}.skill`);
    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      const sizeBytes = archive.pointer();
      let sizeStr;
      if (sizeBytes >= 1024 * 1024) {
        sizeStr = (sizeBytes / (1024 * 1024)).toFixed(1) + 'MB';
      } else {
        sizeStr = Math.ceil(sizeBytes / 1024) + 'KB';
      }
      console.log(`  ${skillName}.skill  (${sizeStr})`);
      resolve();
    });

    archive.on('error', (err) => reject(err));
    archive.pipe(output);

    // Add the directory contents under the skill name as root folder
    archive.directory(skillPath, skillName);
    archive.finalize();
  });
}

async function build() {
  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('Error: skills/ directory not found');
    process.exit(1);
  }

  // Create dist/ if it doesn't exist
  if (!fs.existsSync(DIST_DIR)) {
    fs.mkdirSync(DIST_DIR, { recursive: true });
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  if (skillDirs.length === 0) {
    console.error('Error: No skill directories found in skills/');
    process.exit(1);
  }

  console.log('Building .skill packages:\n');

  for (const skillName of skillDirs) {
    await buildSkill(skillName);
  }

  console.log('\nBuild complete.');
}

build().catch((err) => {
  console.error('Build error:', err);
  process.exit(1);
});
