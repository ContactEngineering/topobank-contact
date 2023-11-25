# Changelog for plugin *topobank-contact*

## 1.2.0 (2023-11-25)

- MAINT: Update to Bootstrap 5

## 1.1.2 (2023-08-21)

- BUG: Fixed resubmitting contact calculations with pressure selection
- BUG: Make sure task modal updates properly when clicking `Run calculation`
- MAINT: More fixes to CSRF injection

## 1.1.1 (2023-08-04)

- BUG: Fixed viewing of contact geometries
- MAINT: Unified CSRF injection

## 1.1.0 (2023-06-11)

- ENH: Unified single page application for analyses, including rewritten
  task status
- ENH: Proper math format of axes labels

## 1.0.2 (2023-04-06)

- BUG: Reverted to old contact mechanics card view

## 1.0.1 (2023-04-06)

- MAINT: Fixes to version discovery

## 1.0.0 (2023-01-31)

- MAINT: Version discovery from VCS

## 0.92.1 (2022-11-11)

- ENH: Made "Tasks" button more prominent in analyses list,
  as for analysis functions using standard plots
- MAINT: Changes because of bokeh 3.0.1, BokehJSONEncoder
  is no more available

## 0.92.0 (2022-10-14)

This is the initial version of the plugin, based on
the code and the functionality of the contact
mechanics calculations in topobank 0.91.1.

Now, as plugin, topobank >= 0.92.0 is needed for usage.
