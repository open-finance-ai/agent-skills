const chalk = require('chalk').default;
const ora = require('ora').default;

function log(message) {
  console.log(message);
}

function success(message) {
  console.log(chalk.green(message));
}

function error(message) {
  console.error(chalk.red(message));
}

function warn(message) {
  console.warn(chalk.yellow(message));
}

function info(message) {
  console.log(chalk.blue(message));
}

function createSpinner(text) {
  return ora({ text });
}

module.exports = { log, success, error, warn, info, createSpinner };
