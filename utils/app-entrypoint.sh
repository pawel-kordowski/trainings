#!/bin/sh
./utils/wait-for db:5432
./utils/wait-for rabbitmq:5672
$@