const { describe, it, before, after } = require('node:test');
const assert = require('node:assert');
const fs = require('fs');
const path = require('path');

const SKILLS_JSON_PATH = path.resolve(__dirname, '../../skills.json');

describe('registry', () => {
  let originalContent;
  let hadFile;

  before(() => {
    hadFile = fs.existsSync(SKILLS_JSON_PATH);
    if (hadFile) {
      originalContent = fs.readFileSync(SKILLS_JSON_PATH, 'utf8');
    }

    const testSkills = [
      {
        name: 'test-skill',
        version: '1.0.0',
        description: 'A test skill',
        category: 'testing',
        tags: ['test'],
        pythonDependencies: [],
      },
      {
        name: 'another-skill',
        version: '2.0.0',
        description: 'Another test skill',
        category: 'testing',
        tags: ['test', 'demo'],
        pythonDependencies: ['numpy'],
      },
    ];

    fs.writeFileSync(SKILLS_JSON_PATH, JSON.stringify(testSkills, null, 2));
  });

  after(() => {
    if (hadFile) {
      fs.writeFileSync(SKILLS_JSON_PATH, originalContent);
    } else {
      fs.unlinkSync(SKILLS_JSON_PATH);
    }
  });

  // Re-require registry in each test to pick up the test data
  function loadRegistry() {
    delete require.cache[require.resolve('../../cli/lib/registry')];
    return require('../../cli/lib/registry');
  }

  it('getSkills returns an array', () => {
    const { getSkills } = loadRegistry();
    const skills = getSkills();
    assert.ok(Array.isArray(skills), 'Expected an array');
    assert.strictEqual(skills.length, 2);
  });

  it('getSkill returns a skill by name', () => {
    const { getSkill } = loadRegistry();
    const skill = getSkill('test-skill');
    assert.ok(skill, 'Expected a skill object');
    assert.strictEqual(skill.name, 'test-skill');
    assert.strictEqual(skill.version, '1.0.0');
    assert.strictEqual(skill.description, 'A test skill');
  });

  it('getSkill returns null for unknown skill', () => {
    const { getSkill } = loadRegistry();
    const skill = getSkill('nonexistent-skill');
    assert.strictEqual(skill, null);
  });

  it('getSkillNames returns array of names', () => {
    const { getSkillNames } = loadRegistry();
    const names = getSkillNames();
    assert.deepStrictEqual(names, ['test-skill', 'another-skill']);
  });
});
