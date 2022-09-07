#!/bin/bash
USER=${1}
PASSWORD=${2}
curl -X 'POST' \
  'http://localhost/api/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d "{
  \"email\": \"${USER}\",
  \"password\": \"${PASSWORD}\",
  \"is_active\": true,
  \"is_superuser\": false,
  \"is_verified\": false
}"
