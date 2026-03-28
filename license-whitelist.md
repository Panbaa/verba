# License Whitelist

## Why This File Exists

This project is intentionally built as a local-first, commercially usable product that should run without sending user data to external services. To keep that goal intact, every dependency must be checked not only for technical fit, but also for license fit.

This file exists so contributors can make consistent decisions before adding new software, models, voices, assets, fonts, or bundled binaries. The goal is to keep the legal surface area small, predictable, and easy to maintain.

In practice, this means:

- We prefer permissive licenses.
- We avoid licenses that create source-sharing, network-use, or redistribution obligations that do not fit the project.
- We review not only code packages, but also model weights, tokenizer files, voice assets, sample media, and any prebuilt binaries.

If a dependency is useful but does not clearly fit this policy, do not add it until the license has been reviewed and documented.

## Project Licensing Goal

The project should remain:

- free to build and use
- commercially usable
- local-first
- simple to redistribute
- low-friction for future packaging and distribution

The project owner is fine with keeping attribution and license notices in the documentation where required. That is acceptable. The project should still avoid dependencies that introduce stronger copyleft or usage restrictions.

## Default Rule

Only add a dependency if its license is explicitly known, documented, and compatible with this whitelist.

If the license is unclear, custom, missing, or contradictory across sources, treat it as not approved.

## Approved Licenses

These licenses are approved by default for code dependencies:

- MIT
- Apache-2.0
- BSD-2-Clause
- BSD-3-Clause
- ISC
- Zlib
- Python-2.0
- 0BSD

These licenses are approved for non-code assets when applicable:

- CC0
- CC-BY, if attribution is documented clearly in the repository

## Conditionally Usable, But Avoid By Default

These licenses can be commercially usable, but they are not preferred for this project because they increase compliance complexity or reduce packaging flexibility:

- LGPL
- MPL-2.0

Dependencies under these licenses should only be used if:

- there is no strong permissive alternative
- the dependency is important to the MVP or production roadmap
- the compliance impact is understood and documented
- the project owner explicitly accepts the tradeoff

## Not Approved

The following license categories are not approved for this project:

- GPL
- AGPL
- SSPL
- BSL
- Commons Clause
- Elastic License
- Polyform licenses
- non-commercial licenses
- research-only licenses
- personal-use-only licenses
- no-derivatives licenses
- field-of-use restricted licenses
- any custom or unclear license that has not been explicitly reviewed

## What Must Be Checked

License review is required for all of the following, not just Python packages:

- application code dependencies
- Python packages
- native libraries
- bundled binaries
- model weights
- tokenizer files
- TTS voice assets
- sample audio or media files
- fonts
- icons
- any downloaded runtime asset used by the app

This matters because AI tooling often uses permissive code with more restrictive model or asset licenses.

## Contributor Rules

Before adding a new dependency or asset:

1. Find the exact license text or the official license declaration.
2. Confirm that commercial use is allowed.
3. Confirm that redistribution is allowed, if the dependency may ship with the app.
4. Confirm that there are no non-commercial, research-only, or field-of-use restrictions.
5. Record the dependency, version, source, and license in the project documentation.

If any of these checks fail, do not add the dependency.

## Documentation Rule

When a dependency is accepted, document:

- name
- version
- source URL or upstream project
- license
- whether attribution or notice retention is required
- whether it is code, model, voice, binary, or asset

## Working Interpretation For This Project

This project may use open-source software that is free of charge and commercially usable, even though the project owner does not exclusively own those third-party components. What matters is that the final project can be built, used, and distributed without payment and without license terms that conflict with the project's goals.

That means:

- permissive open-source software is acceptable
- naming and attributing dependencies in the docs is acceptable
- restrictive copyleft or usage-limited software is not acceptable

## Short Decision Guide

Use this dependency:

- if it is MIT, Apache, BSD, ISC, Zlib, Python-2.0, 0BSD, or an equivalent clearly permissive license
- if its model and asset licenses are also permissive
- if it can run locally without mandatory external services

Do not use this dependency:

- if it is GPL-family, source-available, non-commercial, research-only, or otherwise restrictive
- if the code license is fine but the model or voice license is not
- if the license status cannot be verified from official sources
