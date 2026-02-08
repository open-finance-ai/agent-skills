const { Command } = require('commander');
const { getSkill, getSkillNames } = require('../lib/registry');
const { installSkill, uninstallSkill, isInstalled } = require('../lib/installer');
const { success, error, warn, info, createSpinner } = require('../lib/logger');

const updateCommand = new Command('update')
  .description('Update an installed skill')
  .argument('[name]', 'Skill name')
  .option('-a, --all', 'Update all installed skills')
  .action(async (name, options) => {
    let skillNames;
    if (options.all) {
      skillNames = getSkillNames().filter((n) => isInstalled(n));
    } else if (name) {
      skillNames = [name];
    } else {
      error('Please specify a skill name or use --all.');
      process.exitCode = 1;
      return;
    }

    if (skillNames.length === 0) {
      warn('No installed skills to update.');
      return;
    }

    for (const skillName of skillNames) {
      const skill = getSkill(skillName);
      if (!skill) {
        error(`Skill not found: ${skillName}`);
        process.exitCode = 1;
        return;
      }

      if (!isInstalled(skillName)) {
        warn(`Skill "${skillName}" is not installed. Use "install" first.`);
        continue;
      }

      const spinner = createSpinner(`Updating ${skillName}...`);
      spinner.start();

      try {
        await uninstallSkill(skillName);
        await installSkill(skillName);
        spinner.succeed(`Updated ${skillName}`);

        if (skill.pythonDependencies && skill.pythonDependencies.length > 0) {
          const deps = skill.pythonDependencies.join(' ');
          info('');
          info(
            `  This skill requires Python packages: ${deps}`
          );
          info(`  Install with: pip install ${deps}`);
          info('');
        }
      } catch (err) {
        spinner.fail(`Failed to update ${skillName}`);
        error(`  ${err.message}`);
        process.exitCode = 1;
        return;
      }
    }

    success('Done.');
  });

module.exports = updateCommand;
