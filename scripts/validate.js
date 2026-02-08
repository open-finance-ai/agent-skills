#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.join(__dirname, '..', 'skills');
const MAX_FILE_SIZE = 1024 * 1024; // 1MB

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return null;

  const yaml = match[1];
  const fields = {};
  let currentKey = null;

  for (const line of yaml.split('\n')) {
    const keyMatch = line.match(/^(\w[\w-]*):\s*(.*)/);
    if (keyMatch) {
      currentKey = keyMatch[1];
      const value = keyMatch[2].trim();
      // Handle multi-line scalar (>) or plain value
      if (value === '>' || value === '|') {
        fields[currentKey] = '';
      } else {
        fields[currentKey] = value;
      }
    } else if (currentKey && line.match(/^\s+/)) {
      // Continuation of multi-line value
      const trimmed = line.trim();
      if (trimmed) {
        fields[currentKey] = fields[currentKey]
          ? fields[currentKey] + ' ' + trimmed
          : trimmed;
      }
    }
  }
  return fields;
}

function checkFileSizes(dirPath, errors) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      checkFileSizes(fullPath, errors);
    } else if (entry.isFile()) {
      const stat = fs.statSync(fullPath);
      if (stat.size > MAX_FILE_SIZE) {
        const relPath = path.relative(SKILLS_DIR, fullPath);
        const sizeMB = (stat.size / (1024 * 1024)).toFixed(2);
        errors.push(`File exceeds 1MB: ${relPath} (${sizeMB}MB)`);
      }
    }
  }
}

function validate() {
  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('Error: skills/ directory not found');
    process.exit(1);
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name);

  if (skillDirs.length === 0) {
    console.error('Error: No skill directories found in skills/');
    process.exit(1);
  }

  let hasErrors = false;

  for (const skillName of skillDirs) {
    const skillPath = path.join(SKILLS_DIR, skillName);
    const errors = [];

    console.log(`\nValidating: ${skillName}`);

    // Check SKILL.md exists
    const skillMdPath = path.join(skillPath, 'SKILL.md');
    if (!fs.existsSync(skillMdPath)) {
      errors.push('Missing SKILL.md');
    } else {
      // Check frontmatter
      const content = fs.readFileSync(skillMdPath, 'utf-8');
      const frontmatter = parseFrontmatter(content);
      if (!frontmatter) {
        errors.push('SKILL.md has no valid YAML frontmatter (must be between --- delimiters)');
      } else {
        if (!frontmatter.name) {
          errors.push('SKILL.md frontmatter missing required field: name');
        }
        if (!frontmatter.description) {
          errors.push('SKILL.md frontmatter missing required field: description');
        }
      }
    }

    // Check README.md exists
    const readmePath = path.join(skillPath, 'README.md');
    if (!fs.existsSync(readmePath)) {
      errors.push('Missing README.md');
    }

    // Check file sizes
    checkFileSizes(skillPath, errors);

    if (errors.length > 0) {
      hasErrors = true;
      for (const err of errors) {
        console.log(`  FAIL: ${err}`);
      }
    } else {
      console.log('  PASS');
    }
  }

  console.log('');
  if (hasErrors) {
    console.error('Validation failed.');
    process.exit(1);
  } else {
    console.log('All skills validated successfully.');
  }
}

validate();
