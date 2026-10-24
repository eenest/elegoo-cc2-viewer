# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2026 Eugene Nesterenko
from pathlib import Path
import html
import shutil
import zipfile
import hashlib

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
stage = root / 'work' / 'Elegoo-Viewer-for-Linux-Mint'
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True, exist_ok=True)
package = 'elegoo-viewer_0.6.2_all.deb'
shutil.copy2(out / package, stage / package)
for old in stage.glob('*.deb'):
    if old.name != package:
        old.unlink()
shutil.copy2(root / 'COPYRIGHT', stage / 'COPYRIGHT.txt')
for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md'):
    shutil.copy2(root / name, stage / name)
shutil.copytree(root / 'LICENSES', stage / 'LICENSES', dirs_exist_ok=True)
import tarfile
source_archive = out / 'elegoo-viewer-0.6.2-source.tar.gz'
with tarfile.open(source_archive, 'w:gz') as archive:
    for name in ('viewer.py', 'stream.py', 'discovery.py', 'profiles.py', 'README.md', 'COPYRIGHT', 'LICENSE', 'THIRD_PARTY_NOTICES.md', 'LICENSES', 'assets', 'docs/images', 'packaging', 'tests'):
        archive.add(root / name, arcname='elegoo-viewer-0.6.2/' + name, filter=lambda info: None if '__pycache__' in info.name or info.name.endswith('.pyc') else info)
shutil.copy2(source_archive, stage / source_archive.name)
sections = [
('What this is', '''Elegoo Viewer is a small app for watching your Elegoo Centauri Carbon 2 printer’s camera on your Linux Mint laptop. You do not need to install ElegooSlicer or set up Python. You do not need an Elegoo account for this app.

The app has been installed on Dad’s computer, and his supplied screenshot shows a live CC2 camera view. Your own laptop and printer still need to be checked. IMPORTANT: the printer must be in LAN-only mode on stock ELEGOO firmware, or use compatible CC2 community firmware configured for local camera plus cloud/web access. Stock cloud mode alone will not work.'''),
('1. Before you start', '''• Turn on your printer and let it finish starting.
• Connect the printer and laptop to the same home network. The laptop can use Wi-Fi or a network cable. Avoid a guest Wi-Fi network.
• Keep the laptop connected to the internet during installation, because Linux Mint may need to download supporting software.
• Have your Linux Mint login password ready. This is the password you use for your laptop, not your Wi-Fi or Elegoo password.
• If anything on screen is different from these instructions, stop and send Dad a photo of the screen.'''),
('Required printer mode — read before connecting', '''Choose one supported setup:

A. Original ELEGOO firmware: enable LAN-only mode in the printer touchscreen network settings. Menu names vary by firmware. This can disable the normal cloud/mobile connection.

B. Compatible CC2 community firmware: use a version that supports simultaneous local camera and cloud/web access (LAN/WAN coexistence), and ensure local camera access is enabled. This lets the viewer use the LAN while supported cloud/web features remain available.

Stock cloud mode by itself does not meet this app's requirements. The viewer cannot change this mode for you. Ask Dad for help if you want to keep cloud access or need community firmware; installing this app does not install printer firmware.

Community firmware information: https://github.com/Neme77/centauri-carbon-2-community
Follow that project's compatibility and setup instructions. Keep the laptop and printer on the same reachable home network.'''),
('2. Open the files Dad sent you', '''1. Download and save Elegoo-Viewer-for-Linux-Mint-v0.6.2.zip to your laptop. Your browser will usually put it in Downloads.
2. Open the file manager using the folder icon on the bottom panel, or open Home from the desktop.
3. Click Downloads in the left side of the window.
4. Right-click Elegoo-Viewer-for-Linux-Mint-v0.6.2.zip and choose Extract Here. If that option is absent, double-click the ZIP and use the Extract button in the archive window. Extract it to Downloads.
5. Open the extracted Elegoo-Viewer-for-Linux-Mint folder. You should see the installer and these instructions.

The installer’s full filename is elegoo-viewer_0.6.2_all.deb. The .deb ending means it is an installation package for Linux Mint.'''),
('3. Install the app — only once', '''1. Double-click elegoo-viewer_0.6.2_all.deb inside the extracted folder.
2. Linux Mint should open a package installer window. Its name and appearance depend on your Mint version.
3. Click Install Package or Install. If it says Reinstall, that means this version is already installed; you can use Reinstall.
4. If asked for authentication, enter your laptop login password and approve the installation.
5. If Mint lists additional required packages, allow it to install them.
6. Wait until the installer reports that installation has finished. Do not close the laptop while it is installing.
7. Close the installer window.

If double-clicking shows files inside the package instead of an Install button, close that window. Right-click the .deb file, choose Open With, and select the package installer if offered. If no package installer is listed, ask Dad for help or use the optional terminal instructions at the end.'''),
('4. Open Elegoo Viewer', '''1. Click the Linux Mint menu at the bottom-left of the screen.
2. Type Elegoo Viewer in the menu’s search box.
3. Click Elegoo Viewer in the results.

You should see a printer IP address box, Find printers, Connect, a saved-printer dropdown, and Add printer / Edit / Remove buttons. The large middle area is where the camera picture will appear.

You do not need to open the installer each time you want to use the app.'''),
('5. Find your printer — try this first', '''1. Make sure the printer is on and connected to your home network.
2. Click Find printers.
3. Wait for the search to finish. It normally takes several seconds, but may take longer on some networks.
4. If a result appears in the results dropdown below the IP address box, select it. The printer IP box will be filled in for you.
5. A result marked “likely CC2” is only a possible printer. If more than one appears, compare its IP address with the address shown on your printer’s network screen before connecting. Ask Dad if you are unsure.
6. You may see a long code such as 88:49:2d:xx:xx:xx. This is a MAC address. You do not need to type or change it.
7. Click Connect.
8. If video works, a picture will appear and the status will say Live.

The app automatically saves a printer when you connect. It also remembers the printer’s MAC address when available, which can help find it if its IP changes later.

If the search finds nothing, continue with step 6. That does not necessarily mean your printer is broken.'''),
('6. Enter the IP yourself if search does not find it', '''1. On the printer’s touchscreen, open Settings and look for Network or Wi-Fi information. The exact menu names depend on the printer firmware.
2. Find the printer’s IP address. It looks like four numbers separated by dots, for example 192.168.1.33.
3. In Elegoo Viewer, click inside the printer IP address box. Press Ctrl+A to select any existing text, then type the printer’s actual IP address, including the dots.
4. Enter only the IP address. Do not add http://, a port number, or a password.
5. Click Connect.

192.168.1.33 above is only an example. Do not use Dad’s printer address; use the one on your own printer screen. If you cannot find the address, send Dad a photo of the printer’s network screen.'''),
('7. Give it a name or add more printers', '''To name a printer you have already connected to:
1. Choose it from the top saved-printer dropdown.
2. Click Edit.
3. Enter a simple name such as My CC2 or Workshop printer.
4. Leave the IP address as it is unless the printer’s address changed.
5. Click Save.

To add another printer:
1. Click Add printer.
2. Enter a name and that printer’s IP address.
3. Click Save.
4. Choose it from the saved-printer dropdown and click Connect.

You can also find the new printer with Find printers, select its search result, and then click Add printer to name and save it.

The app shows one camera at a time. Choosing another saved printer disconnects the current view; click Connect to start viewing the selected printer.

Remove deletes the selected printer only from this app’s saved list. It does not delete anything on the physical printer.'''),
('8. Next time you use it', '''1. Turn on the printer and connect your laptop to the home network.
2. Open Elegoo Viewer from the Mint menu.
3. Select your printer from the saved-printer dropdown.
4. Click Connect.
5. Click Disconnect when you are finished, or close the window.

If it worked before but no longer connects, click Find printers again. Your router may have assigned a new IP address. If the app recognizes the saved MAC, connecting to that result updates the saved IP. Otherwise check the IP on the printer and update it using Edit.'''),
('Save a camera screenshot', '''1. Connect to your printer and wait until the live camera picture appears.
2. Click Save screenshot. The button is unavailable until the app receives a camera frame.
3. A save window opens. The picture is captured when you click Save screenshot, even if the live video keeps moving afterward.
4. Choose a folder, such as Pictures. Keep the suggested date-and-time filename or enter your own name ending in .png.
5. Click Save. If asked to replace an existing file, choose carefully; replacing overwrites that file.
6. Open your file manager and look in the folder you selected to see the picture.

The screenshot contains the camera picture at its original resolution, not the app controls or the whole laptop screen.'''),
('9. If there is no picture', '''If the app opens, installation has succeeded. No picture is a separate connection or camera issue.

Try these steps:
1. Check that the printer is powered on and connected to Wi-Fi.
2. Check that laptop and printer are on the same home network, rather than guest Wi-Fi.
3. Compare the IP in the app with the current IP on the printer screen.
4. Click Disconnect if available, then Connect to retry.
5. Read the message at the bottom of the app. Send Dad a photo showing that message and the IP address box if you need help.

If the message says Video unavailable or the connection times out, the printer may not be providing local video. Stock ELEGOO firmware requires LAN-only mode. To keep local camera plus cloud/web access, use compatible community firmware with that feature enabled. The app cannot turn that stream on by itself.

Before changing printer network mode or firmware, ask Dad for help. LAN-only mode can affect cloud/mobile access. If your existing mobile camera app works, you can continue using it while Dad checks the local connection.

If search finds no devices, manual IP entry can still work. Search may be blocked by network settings or by the printer’s local ports being disabled.'''),
('About and copyright', '''Click About near the top of Elegoo Viewer to see its version, author, and copyright information. Copyright © 2026 Eugene Nesterenko. Licensed under GNU GPL version 3. This is an independent project, not an official ELEGOO app.'''),
('10. Installing a newer version later', '''Dad can send you a new .deb installer. Download it, double-click it, and choose Install or Upgrade. Close Elegoo Viewer before updating, then reopen it afterward. Saved printers should remain available. You do not need to uninstall first.'''),
('Optional: terminal installation — only if the normal installer fails', '''You can ask Dad to help with this section.

1. Open the extracted folder containing the .deb installer.
2. Right-click empty space in that folder and choose Open in Terminal if available.
3. Paste the following line into the terminal and press Enter:

sudo apt install ./elegoo-viewer_0.6.2_all.deb

4. If asked for your password, type your laptop login password and press Enter. The terminal shows no letters or dots while you type; this is normal.
5. If asked whether to continue, type Y and press Enter.
6. Wait until the installation finishes and the normal command prompt returns. Then close the terminal and open Elegoo Viewer from the Mint menu.

If an error appears, send Dad a photo of the entire terminal window. Do not try random commands from the internet.'''),
]
text='ELEGOO VIEWER — LINUX MINT GUIDE\nVersion 0.6.2\n\n'+'\n\n'.join(title+'\n'+'='*len(title)+'\n'+body for title,body in sections)+'\n'
(stage/'START-HERE.txt').write_text(text)
body=''.join('<section><h2>'+html.escape(title)+'</h2>'+''.join('<p>'+html.escape(p).replace('\n','<br>')+'</p>' for p in content.split('\n\n'))+'</section>' for title,content in sections)
guide='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Elegoo Viewer — Start Here</title><style>body{font:18px/1.65 system-ui,sans-serif;color:#172334;background:#edf2f7;margin:0}main{max-width:850px;margin:auto;background:white;padding:40px}h1{line-height:1.2;color:#155d70}h2{font-size:24px;line-height:1.3}section{border-top:1px solid #d9e1e8;margin-top:30px;padding-top:12px}p{overflow-wrap:anywhere}@media print{body{background:white}main{padding:0}h2{break-after:avoid}p{orphans:3;widows:3}}</style><main><h1>Elegoo Viewer<br>Start here</h1><p>Linux Mint • Version 0.6.2<br>Install once, then open the app from the Mint menu.</p>'''+body+'</main></html>'
(stage/'START-HERE.html').write_text(guide)
(stage/'SHA256SUMS.txt').write_text(hashlib.sha256((stage/package).read_bytes()).hexdigest()+'  '+package+'\n')
zip_path=out/'Elegoo-Viewer-for-Linux-Mint-v0.6.2.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
 for file in sorted(stage.rglob('*')):
  if file.is_file():
   z.write(file,stage.name+'/'+str(file.relative_to(stage)))
with zipfile.ZipFile(zip_path) as z:
 assert z.testzip() is None
 assert z.read(stage.name+'/'+package)==(out/package).read_bytes()
shutil.copy2(stage/'START-HERE.html',out/'Elegoo-Viewer-Start-Here.html')
shutil.copy2(stage/'START-HERE.txt',out/'Elegoo-Viewer-Start-Here.txt')
print('Created and verified:',zip_path)
print('Included:', ', '.join(p.name for p in sorted(stage.iterdir())))
