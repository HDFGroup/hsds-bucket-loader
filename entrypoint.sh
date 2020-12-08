#!/bin/bash
echo "bucket-loader entrypoint"
export PYTHONUNBUFFERED="1"
cd /app
if [ ${RUN_COMMAND} ]; then
  echo "run_command: ${RUN_COMMAND} "
  if [ ${RUN_COMMAND} == "diff" ]; then
    python diff_files.py
  elif [ ${RUN_COMMAND} == "load" ]; then
    python loadfiles.py
  elif [ ${RUN_COMMAND} == "watch" ]; then
    python watchdog.py
  elif [ ${RUN_COMMAND} == "dump" ]; then
    python dump_inventory_file.py
  elif [ ${RUN_COMMAND} == "make" ]; then
    python make_inventory_file.py
  elif [ ${RUN_COMMAND} == "bash" ]; then
    bash
  else
    exit "Unexpected RUN_COMMAND: ${RUN_COMMAND}"
  fi
else
  bash
fi
