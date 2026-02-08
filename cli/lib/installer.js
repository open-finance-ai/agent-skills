const fs = require('fs');
const path = require('path');
const extractZip = require('extract-zip');

const SKILLS_DIR = path.join(
  process.env.HOME || process.env.USERPROFILE,
  '.claude',
  'skills'
);

const DIST_DIR = path.resolve(__dirname, '../../dist');

function getInstallPath(skillName) {
  return path.join(SKILLS_DIR, skillName);
}

function isInstalled(skillName) {
  const installPath = getInstallPath(skillName);
  return fs.existsSync(path.join(installPath, 'SKILL.md'));
}

async function installSkill(skillName) {
  const zipPath = path.join(DIST_DIR, `${skillName}.skill`);
  if (!fs.existsSync(zipPath)) {
    throw new Error(`Skill package not found: ${zipPath}`);
  }

  const targetDir = getInstallPath(skillName);

  // Clean up existing installation
  if (fs.existsSync(targetDir)) {
    fs.rmSync(targetDir, { recursive: true, force: true });
  }

  // Extract to a temp directory first, then move contents up
  // The ZIP contains skillName/ as root, so we extract to parent
  // and the ZIP creates skillName/ automatically
  const parentDir = SKILLS_DIR;
  fs.mkdirSync(parentDir, { recursive: true });

  await extractZip(zipPath, { dir: parentDir });
}

async function uninstallSkill(skillName) {
  const targetDir = getInstallPath(skillName);
  if (!fs.existsSync(targetDir)) {
    throw new Error(`Skill is not installed: ${skillName}`);
  }
  fs.rmSync(targetDir, { recursive: true, force: true });
}

module.exports = { installSkill, uninstallSkill, isInstalled, getInstallPath };
