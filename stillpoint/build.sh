#!/usr/bin/env bash
# Wraps app.html (the artifact source) into a standalone index.html for GitHub Pages / home-screen install.
cd "$(dirname "$0")"
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="theme-color" content="#3B5A7D">\n<link rel="manifest" href="manifest.webmanifest">\n<link rel="icon" href="icon.svg">\n<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}img{max-width:100%%}</style>\n</head>\n<body>\n'; cat app.html; printf '\n</body>\n</html>\n'; } > index.html
