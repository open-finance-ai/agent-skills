const { Command } = require('commander');
const { getSkills } = require('../lib/registry');
const { isInstalled } = require('../lib/installer');
const { log, warn } = require('../lib/logger');
const chalk = require('chalk').default;

const listCommand = new Command('list')
  .description('List all available skills')
  .action(() => {
    const skills = getSkills();

    if (skills.length === 0) {
      warn('No skills found. Run the build first to generate skills.json.');
      return;
    }

    const nameWidth = 30;
    const descWidth = 50;
    const statusWidth = 12;

    log('');
    log(
      chalk.bold(
        'Name'.padEnd(nameWidth) +
          'Description'.padEnd(descWidth) +
          'Status'.padEnd(statusWidth)
      )
    );
    log('-'.repeat(nameWidth + descWidth + statusWidth));

    for (const skill of skills) {
      const installed = isInstalled(skill.name);
      const status = installed
        ? chalk.green('installed')
        : chalk.gray('not installed');
      const description =
        skill.description.length > descWidth - 2
          ? skill.description.slice(0, descWidth - 5) + '...'
          : skill.description;

      log(
        skill.name.padEnd(nameWidth) +
          description.padEnd(descWidth) +
          status
      );
    }

    log('');
  });

module.exports = listCommand;
