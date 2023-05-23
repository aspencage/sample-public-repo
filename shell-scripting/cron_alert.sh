#!/bin/sh
# purpose: send an email periodically when automated with a cron job to avoid accidentally leaving an on-demand ec2 instance running
t=$(TZ="America/Los_Angeles" date)
e=EMAIL_ADDRESS_HERE
msg_="Orbweaver is online and spinning a web 🕷 🕸 🔮  ("$t"). Do you still need it?"
subj_="IT'S ALIVE!🕷 🕸 🔮"
echo $msg_ | mail -s "$subj_" $e