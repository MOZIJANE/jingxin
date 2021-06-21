const rm = require('rimraf');
const chalk = require('chalk');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');

const trunkPath = path.resolve(__dirname, '../..');
const trunkModules = fs.readdirSync(trunkPath);
const pagesPath = path.resolve(__dirname, '../src/pages');
const files = fs.readdirSync(pagesPath);

if (process.platform.startsWith('win')) {
  console.log(chalk.red('cp command fail on window system, pls use linux! \n'));
} else {
  files.forEach((file) => {
    const filePath = path.resolve(pagesPath, file);
    const stats = fs.statSync(filePath);
    if (stats.isDirectory() && trunkModules.includes(file)) {
      const pagesInModule = path.resolve(trunkPath, file, './pages');
      rm(pagesInModule, err => {
        if (!err) {
          console.log(chalk.cyan(pagesInModule, ' removed! \n'));
          copy(filePath, path.resolve(trunkPath, file));
          fs.rename(path.resolve(trunkPath, file, file), path.resolve(trunkPath, file, 'pages'), (err) => {
            !err && console.log(chalk.green(file, ' pages successfully copyed! \n'));
          });
        }
      });
    }
  });
}

function copy(from , to) {
  spawnSync('cp', ['-r', from, to]);
}
