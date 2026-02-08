#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const SKILLS_DIR = path.join(__dirname, '..', 'skills');
const DIST_DIR = path.join(__dirname, '..', 'dist');
const OUTPUT_PATH = path.join(__dirname, '..', 'skills.json');

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};

  const yaml = match[1];
  const fields = {};
  let currentKey = null;

  for (const line of yaml.split('\n')) {
    const keyMatch = line.match(/^(\w[\w-]*):\s*(.*)/);
    if (keyMatch) {
      currentKey = keyMatch[1];
      const value = keyMatch[2].trim();
      if (value === '>' || value === '|') {
        fields[currentKey] = '';
      } else {
        fields[currentKey] = value;
      }
    } else if (currentKey && line.match(/^\s+/)) {
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

function formatFileSize(bytes) {
  if (bytes >= 1024 * 1024) {
    return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
  }
  return Math.ceil(bytes / 1024) + 'KB';
}

function readRequirements(skillPath) {
  const reqPath = path.join(skillPath, 'scripts', 'requirements.txt');
  if (!fs.existsSync(reqPath)) return [];
  return fs.readFileSync(reqPath, 'utf-8')
    .split('\n')
    .map(line => line.trim())
    .filter(line => line && !line.startsWith('#'));
}

function getFileSize(skillName) {
  const zipPath = path.join(DIST_DIR, `${skillName}.skill`);
  if (!fs.existsSync(zipPath)) return 'unknown';
  const stat = fs.statSync(zipPath);
  return formatFileSize(stat.size);
}

// Skill-specific metadata overrides for known skills
const SKILL_METADATA = {
  'bank-account-analysis': {
    description: 'Israeli bank account analysis with Hebrew PDF reports',
    descriptionHe: 'ניתוח חשבון בנק עם דוחות PDF בעברית',
    category: 'finance',
    tags: ['banking', 'israel', 'hebrew', 'pdf'],
  },
};

function generateManifest() {
  if (!fs.existsSync(SKILLS_DIR)) {
    console.error('Error: skills/ directory not found');
    process.exit(1);
  }

  const skillDirs = fs.readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => d.name)
    .sort();

  const skills = skillDirs.map((skillName) => {
    const skillPath = path.join(SKILLS_DIR, skillName);
    const skillMdPath = path.join(skillPath, 'SKILL.md');

    let frontmatter = {};
    if (fs.existsSync(skillMdPath)) {
      const content = fs.readFileSync(skillMdPath, 'utf-8');
      frontmatter = parseFrontmatter(content);
    }

    const overrides = SKILL_METADATA[skillName] || {};

    const entry = {
      name: frontmatter.name || skillName,
      version: frontmatter.version || '1.0.0',
      description: overrides.description || frontmatter.description || '',
      descriptionHe: overrides.descriptionHe || frontmatter.descriptionHe || '',
      category: overrides.category || frontmatter.category || 'general',
      tags: overrides.tags || (frontmatter.tags ? frontmatter.tags.split(',').map(t => t.trim()) : []),
      pythonDependencies: readRequirements(skillPath),
      fileSize: getFileSize(skillName),
    };

    // Remove empty optional fields
    if (!entry.descriptionHe) delete entry.descriptionHe;
    if (entry.tags.length === 0) delete entry.tags;
    if (entry.pythonDependencies.length === 0) delete entry.pythonDependencies;

    return entry;
  });

  const manifest = {
    version: '1.0.0',
    skills,
  };

  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(manifest, null, 2) + '\n', 'utf-8');
  console.log(`Generated skills.json with ${skills.length} skill(s).`);
}

generateManifest();
