#!/bin/bash

# Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
# Copyleft - 2026 Gianluca Pernigotto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: July.11.2025
#
# Purpose: Delete obsolete translation messages on vidtuber.po files
#          for each locale found on the TARGET directory.
#
# USAGE: ~$ cd /Vidtuber/source/directory
#        ~$ develop/gettext_utils/purge_deleted_translation.sh

TARGET="vidtuber/data/locale"  # relative path to "locale" directory

echo -e "\nTarget directory: \033[34m\e[1m'${TARGET}'\e[0m"

if [ ! -d "${TARGET}" ]; then
    echo -e "\033[31mERROR:\e[0m Directory does not exist: '${TARGET}'"
    exit 1
fi

for langdirs in $(ls -d ${TARGET}/*/)
do
    PO="${langdirs}LC_MESSAGES/vidtuber.po"
    msgattrib --output-file="${PO}" --no-obsolete "${PO}"
    if [[ $? -ne 0 ]]; then
        echo -e '\e[1m\033[31mFailed!\e[0m'
        exit $?
    fi
    echo "INFO: Deleting obsolete: '"${PO}"' ...OK"
done

echo -e "\n\e[1mSuccessfully updated.\e[0m"
echo -e "\033[32mDone!\e[0m"
