#!/bin/sh

echo "zipping files for aws beanstalk"
zip -u zip/payload.zip .ebextensions/cron-linux.config api.key application.py key.json source.py requirements.txt timeseries.py
echo "done."