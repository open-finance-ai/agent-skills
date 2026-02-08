const { Command } = require('commander');
const { getSkill } = require('../lib/registry');
const { isInstalled, getInstallPath } = require('../lib/installer');
const { log, error, info } = require('../lib/logger');
const chalk = require('chalk').default;

const infoCommand = new Command('info')
  .description('Show detailed information about a skill')
  .argument('<name>', 'Skill name')
  .action((name) => {
    const skill = getSkill(name);

    if (!skill) {
      error(`Skill not found: ${name}`);
      process.exitCode = 1;
      return;
    }

    const installed = isInstalled(name);

    log('');
    log(chalk.bold(`  ${skill.name}`));
    log('');
    log(`  ${'Version:'.padEnd(20)} ${skill.version || 'N/A'}`);
    log(`  ${'Description:'.padEnd(20)} ${skill.description}`);
    log(`  ${'Category:'.padEnd(20)} ${skill.category || 'N/A'}`);

    if (skill.tags && skill.tags.length > 0) {
      log(`  ${'Tags:'.padEnd(20)} ${skill.tags.join(', ')}`);
    }

    if (skill.pythonDependencies && skill.pythonDependencies.length > 0) {
      log(
        `  ${'Python deps:'.padEnd(20)} ${skill.pythonDependencies.join(', ')}`
      );
    }

    if (skill.fileSize) {
      log(`  ${'File size:'.padEnd(20)} ${skill.fileSize}`);
    }

    log('');
    if (installed) {
      log(chalk.green(`  Status: Installed`));
      info(`  Path: ${getInstallPath(name)}`);
    } else {
      log(chalk.gray(`  Status: Not installed`));
    }
    log('');
  });

module.exports = infoCommand;
