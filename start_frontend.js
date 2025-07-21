#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Iniciando TecnoCursos AI Frontend...');

const frontendProcess = spawn('npm', ['start'], {
  stdio: 'inherit',
  cwd: __dirname
});

frontendProcess.on('close', (code) => {
  console.log(`Frontend finalizado com código ${code}`);
});

process.on('SIGINT', () => {
  console.log('\n🛑 Finalizando frontend...');
  frontendProcess.kill('SIGINT');
  process.exit(0);
});