#!/usr/bin/env sh
PROTOS_SRC=.

# PYTHON SECTION
PROTOS_OUT_PY=./py

mkdir -p ${PROTOS_OUT_PY}
protoc -I=${PROTOS_SRC} --python_out=${PROTOS_OUT_PY} ${PROTOS_SRC}/*.proto
for file in ${PROTOS_OUT_PY}/*_pb2.py; do
    [[ -e "$file" ]] || continue
    sed -i -r 's/^\(.*\)_pb2 as \(.*\)$/from . \1_pb2 as \2/g' ${file}
done

/bin/cp -rf ${PROTOS_SRC}/enums.py ${PROTOS_OUT_PY}/enums.py
touch ${PROTOS_OUT_PY}/__init__.py
