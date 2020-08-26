#!/bin/bash

psql $* --no-psqlrc \
     --command="create role test login encrypted password 'test'" \
     --command="comment on role test is 'Owner of the spending database'" \
     --command="create database spending owner test encoding utf8" \
     --command="alter database spending set search_path to ''"

psql $* --no-psqlrc --dbname="spending" \
     --command="drop schema if exists public" \
     --command="create schema tbl" \
     --command="alter schema tbl owner to test" \
     --command="create schema api" \
     --command="alter schema api owner to test"
