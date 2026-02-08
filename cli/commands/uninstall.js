const { Command } = require('commander');
const { getSkill } = require('../lib/registry');
const { uninstallSkill, isInstalled, getInstallPath } = require('../lib/installer');
const { success, error, warn, createSpinner } = require('../lib/logger');

const uninstallCommand = new Command('uninstall')
  .description('Uninstall a skill')
  .argument('<name>', 'Skill name')
  .action(async (name) => {
    const skill = getSkill(name);
    if (!skill) {
      error(`Skill not found: ${name}`);
      process.exitCode = 1;
      return;
    }

    if (!isInstalled(name)) {
      warn(`Skill "${name}" is not installed.`);
      return;
    }

    const spinner = createSpinner(`Uninstalling ${name}...`);
    spinner.start();

    try {
      await uninstallSkill(name);
      spinner.succeed(`Uninstalled ${name}`);
      success(`Removed ${getInstallPath(name)}`);
    } catch (err) {
      spinner.fail(`Failed to uninstall ${name}`);
      error(`  ${err.message}`);
      process.exitCode = 1;
    }
  });

module.exports = uninstallCommand;
