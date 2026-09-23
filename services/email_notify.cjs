'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { createRequire } = require('node:module');

async function main() {
  const message = JSON.parse(fs.readFileSync(0, 'utf8'));
  if (!/^[^\s@,;<>]+@[^\s@,;<>]+\.[^\s@,;<>]+$/.test(message.to)) {
    throw new Error('Invalid notification recipient');
  }
  if (!['SMTP_SERVICE', 'SMTP_EMAIL', 'SMTP_PASSWORD'].every(k => process.env[k])) {
    throw new Error('SMTP configuration missing');
  }
  const qinglongRequire = createRequire(path.resolve(__dirname, '../../sendNotify.js'));
  const nodemailer = qinglongRequire('nodemailer');
  const transport = nodemailer.createTransport({
    service: process.env.SMTP_SERVICE,
    auth: { user: process.env.SMTP_EMAIL, pass: process.env.SMTP_PASSWORD },
    connectionTimeout: 15000, greetingTimeout: 15000, socketTimeout: 20000,
  });
  try {
    const info = await transport.sendMail({
      from: { name: process.env.SMTP_NAME || 'Library Booking', address: process.env.SMTP_EMAIL },
      to: message.to,
      subject: message.subject,
      text: message.body,
    });
    if (!info.accepted?.some(address => address.toLowerCase() === message.to.toLowerCase())) {
      throw new Error('Recipient not accepted');
    }
    console.log('Notification accepted by SMTP server.');
  } finally {
    transport.close();
  }
}
main().catch(() => {
  // Never log SMTP authentication fields or server responses containing addresses.
  console.error('Email delivery failed; check Qinglong SMTP configuration.');
  process.exitCode = 1;
});
