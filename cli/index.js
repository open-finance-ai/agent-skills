#!/usr/bin/env node

const { Command } = require('commander');
const { version, description } = require('../package.json');

const listCommand = require('./commands/list');
const infoCommand = require('./commands/info');
const installCommand = require('./commands/install');
const updateCommand = require('./commands/update');
const uninstallCommand = require('./commands/uninstall');

const program = new Command();

program
  .name('openfinance-skills')
  .description(description)
  .version(version);

program.addCommand(listCommand);
program.addCommand(infoCommand);
program.addCommand(installCommand);
program.addCommand(updateCommand);
program.addCommand(uninstallCommand);

program.parseAsync(process.argv);
