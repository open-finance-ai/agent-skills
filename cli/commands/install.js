const { Command } = require('commander');
const { getSkill, getSkillNames } = require('../lib/registry');
const { installSkill, isInstalled } = require('../lib/installer');
const { success, error, warn, info, createSpinner } = require('../lib/logger');

const installCommand = new Command('install')
  .description('Install a skill')
  .argument('[name]', 'Skill name')
  .option('-a, --all', 'Install all available skills')
  .action(async (name, options) => {
    const skillNames = options.all ? getSkillNames() : name ? [name] : [];

    if (skillNames.length === 0) {
      error('Please specify a skill name or use --all.');
      process.exitCode = 1;
      return;
    }

    for (const skillName of skillNames) {
      const skill = getSkill(skillName);
      if (!skill) {
        error(`Skill not found: ${skillName}`);
        process.exitCode = 1;
        return;
      }

      if (isInstalled(skillName)) {
        warn(`Skill "${skillName}" is already installed. Use "update" to reinstall.`);
        continue;
      }

      const spinner = createSpinner(`Installing ${skillName}...`);
      spinner.start();

      try {
        await installSkill(skillName);
        spinner.succeed(`Installed ${skillName}`);

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
        spinner.fail(`Failed to install ${skillName}`);
        error(`  ${err.message}`);
        process.exitCode = 1;
        return;
      }
    }

    success('Done.');
  });

module.exports = installCommand;
