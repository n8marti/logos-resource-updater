### Workaround for updating Logos resources
Logos includes app updates along with resource updates. The app updates are auto-
installed, and these are frequently incompatible with the existing wine
installation.

1. Download the resources outside of Logos
1. Ideally, put them on an external drive
1. Note the corresponding drive letter in the wine prefix (e.g. "E:")
1. Open Logos, in the Go box type "Scan E:"

Notes:
- This method will download the full resource file, whereas Logos' own
  update process will only download a "patch" file of differences. So this
  method will help you avoid unwanted app updates, but it will not
  likely save you any download data and may very well require more.
- It's not terribly obvious which letter has been assigned to a given external
  drive. This can be found, however, in `$WINEPREFIX/dosdevices`.
- The "Scan" command seems to scan the entire drive, so if the downloaded
  resources are on your system drive, this could potentially take a long time.
  This is why an external drive is recommended.
