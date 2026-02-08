const fs = require('fs');
const path = require('path');

const SKILLS_JSON_PATH = path.resolve(__dirname, '../../skills.json');

function loadSkills() {
  if (!fs.existsSync(SKILLS_JSON_PATH)) {
    return [];
  }
  const data = fs.readFileSync(SKILLS_JSON_PATH, 'utf8');
  const parsed = JSON.parse(data);
  // Support both plain array and { skills: [...] } format
  return Array.isArray(parsed) ? parsed : parsed.skills || [];
}

function getSkills() {
  return loadSkills();
}

function getSkill(name) {
  const skills = loadSkills();
  return skills.find((s) => s.name === name) || null;
}

function getSkillNames() {
  const skills = loadSkills();
  return skills.map((s) => s.name);
}

module.exports = { getSkills, getSkill, getSkillNames };
