#!/bin/bash

python3 -m preview_generator --check-dependencies

exec "$@"