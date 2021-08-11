---
title: Additional Install instructions
author: Brandon J. Nelson
---

## Additional Dependencies for Mac

The ELISA tool prints out reports using weasyprint, which for [Mac has special install instruction](https://doc.courtbouillon.org/weasyprint/latest/first_steps.html#macos). The following packages need to be installed with [Homebrew](https://brew.sh/):

0. If Homebrew is not installed, it can be installed by running the following in terminal:
    - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

1. Now install the necessary packages: `brew install python pango libffi`

## Needs more documentation
