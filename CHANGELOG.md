# Changelog for plugin *topobank-contact*

<!--
Style for this changelog (keep to it so entries stay uniform):

- Newest version first. Heading `vX.Y.Z (DDMonYY)`, underlined with dashes.
  A version not yet released is headed `vX.Y.Z (not yet released)`.
- One bullet per user-visible change, at most two lines (about 200
  characters). Say what changed for the user and, if useful, why or by how
  much. Omit internals: no function, class, file or variable names, no
  environment variables, no commit or PR references.
- Start every bullet with one of: `ENH:` (new feature), `BUG:` (fix),
  `API:` (interface change), `PERF:` (speed or memory), `MAINT:`, `TST:`,
  `DOC:`, `BUILD:`, `CI:`.
- Small related fixes may share one bullet. No trailing period on bullets.
-->

v1.9.0 (02Aug26)
----------------

- ENH: An optional elastic modulus, with its unit, shows the pressure axes of
  derived plots in physical units
- ENH: Contacting points and contact areas come from the solver's set of active
  constraints instead of from a threshold on the forces
- ENH: The per-step result files report the rigid body displacement and whether
  the step converged, and are annotated with units
- ENH: Results include total forces, scan area and rms height, so loads rather
  than nominal pressures can be shown for nonperiodic calculations
- ENH: The workflow has a description and a reference link for display in the
  user interface
- BUG: Measurements with zero rms height raise a clear error instead of yielding
  NaN results
- BUG: The number of steps and the list of pressures are validated
- BUG: The warning about a periodicity mismatch no longer crashes the
  calculation; it names the measurement as plain text
- DOC: Documented geometry and sign conventions, x/y orientation, the definition
  of E* and load control, with a kinematics figure and an example script
- DOC: Documented how to treat the contact of two rough surfaces through a
  composite roughness
- DOC: Documented the contents of the downloadable results of a contact
  calculation
- MAINT: The contact mechanics workflow records the time taken by each step
- MAINT: Updated for the split of the REST API from topobank, the removal of the
  plugin architecture and plugin permissions, and the renaming of folders
- BUILD: Changed build system to hatchling

v1.8.0 (16Dec25)
----------------

- MAINT: Updated for API changes in topobank 1.66.0

v1.7.1 (19Aug25)
----------------

- MAINT: Removed an unused setting for local media storage

v1.7.0 (17Mar25)
----------------

- MAINT: Updated for API changes in topobank 1.57.0
- MAINT: Moved all frontend code to ce-ui

v1.6.0 (11Feb25)
----------------

- MAINT: Updated for API changes in topobank 1.55.0
- MAINT: Analysis workflows are now referred to by unique names
- BUG: Fixed switching between a number of steps and explicit pressures

v1.5.0 (22Dec24)
----------------

- MAINT: Requires ContactMechanics 1.6.0

v1.4.2 (27Nov24)
----------------

- BUG: The parameter dialog stores and restores the choice between periodic
  and free boundaries under the name the API expects
- BUG: Invalid contact mechanics parameters are rejected as a bad request

v1.4.1 (13Nov24)
----------------

- BUG: Results again record where the data of each step is stored
- BUG: Fixed showing the details of a contact mechanics calculation

v1.4.0 (13Nov24)
----------------

- MAINT: Updated for API changes in topobank 1.50.0

v1.3.3 (14May24)
----------------

- ENH: Easier input of pressure values and better validation

v1.3.2 (13May24)
----------------

- BUG: Fixed unit conversion in the plots of contact mechanics distributions

v1.3.1 (13May24)
----------------

- BUG: Fixed pressure input

v1.3.0 (12May24)
----------------

- ENH: Contact mechanics results are shown in the new common analysis card
- MAINT: Uses bootstrap-vue-next components throughout
- MAINT: Updated to ContactMechanics 1.2.5

v1.2.4 (22Mar24)
----------------

- BUG: Fixed detection of the package version

v1.2.3 (21Mar24)
----------------

- BUILD: Changed build system to flit

v1.2.2 (12Mar24)
----------------

- MAINT: Compatibility with topobank 1.7.0

v1.2.1 (20Jan24)
----------------

- MAINT: Updated to ContactMechanics 1.2.2
- MAINT: Code follows PEP 8 style

v1.2.0 (25Nov23)
----------------

- MAINT: Updated to Bootstrap 5

v1.1.2 (21Aug23)
----------------

- BUG: Fixed resubmitting contact calculations with a pressure selection
- BUG: The task dialog updates properly after clicking Run calculation
- MAINT: Further fixes to how the CSRF token is passed to requests

v1.1.1 (04Aug23)
----------------

- BUG: Fixed viewing of contact geometries
- MAINT: Unified how the CSRF token is passed to requests

v1.1.0 (11Jun23)
----------------

- ENH: Unified single page application for analyses, including a rewritten
  task status
- ENH: Axis labels are typeset as proper math

v1.0.2 (06Apr23)
----------------

- BUG: Reverted to the old contact mechanics card view

v1.0.1 (06Apr23)
----------------

- MAINT: Fixes to the detection of the package version

v1.0.0 (31Jan23)
----------------

- MAINT: The package version is taken from version control

v0.92.1 (11Nov22)
-----------------

- ENH: Made the Tasks button more prominent in the analyses list, as for
  analyses using standard plots
- MAINT: Adapted to bokeh 3.0.1

v0.92.0 (14Oct22)
-----------------

- MAINT: Initial version of the plugin, based on the contact mechanics
  calculations of topobank 0.91.1; requires topobank 0.92.0 or newer
