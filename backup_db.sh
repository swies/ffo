#!/bin/sh
mysqldump --single-transaction --quick --extended-insert ffo | bzip2
