=========================================
 Super Mario Galaxy 1 GamePad Hack, v1.2
=========================================

This is a modification of Super Hackio's Super Mario Galaxy Classic Controller
hack, as seen on YouTube:
    https://www.youtube.com/watch?v=0evN_8UFGjA

This version is suitable for use with Wii U VC injection for GamePad input. It
is compatible with the four official releases of Super Mario Galaxy on Wii:

- RMGE01 (USA)
- RMGP01 (Europe)
- RMGJ01 (Japan)
- RMGK01 (Korea)

Note: only USA and Europe versions have been tested by the author on hardware.

Getting this hack up and running on Wii U took a lot more effort than the Super
Mario Galaxy 2 hack, because this hack is re-using an area in memory which is
also used by the Gecko code handler. The Wii U VC version of this hack is made
entirely with Gecko/Ocarina codes, so the Classic Controller hack had to be
relocated in memory to prevent them clashing.

--------------
 Requirements
--------------

To apply the patch, you will need the following:

    Wiimm's wit (https://wit.wiimm.de/download.html)
        if you don't know which version to download,
        you probably want 'Cygwin/64-bit (Windows)'

    Wiimm's wstrt (https://szs.wiimm.de/download.html)
        if you don't know which version to download,
        you probably want 'Cygwin/64-bit (Windows)'

    any Wii VC injection tool, such as:
        UWUVCI-AIO-WPF
            https://github.com/stuff-by-3-random-dudes/UWUVCI-AIO-WPF/releases
        TeconmoonWiiVCInjector
            https://github.com/piratesephiroth/TeconmoonWiiVCInjector/releases

    a disc image of Super Mario Galaxy in any format supported by wit
    (ISO, WDF, WIA, CISO, WBFS)
        NKIT is not supported by wit

----------
 Contents
----------

This archive includes the following files. The RMGx files come in four regional
versions (E, P, J, K) and four preference variants (AllStars or Nvidia layout
and standard or deflicker-filter disabled).

    Mapping-SMG-AllStars.png
        Super Hackio's instructional image showing the button layout you'll get
        if you use one of the All-Stars-style hacks

    Mapping-SMG-Nvidia.png
        Super Hackio's instructional image showing the button layout you'll get
        if you use one of the Nvidia-style hacks

    readme.txt
        this file

    RMGx01.txt
        All of the codes from this modification in text form, in case they're
        useful to you

    RMGx01-AllStars.gct
        a GCT (packaged up cheat file) which can be applied to your game's
        main.dol to give you the All-Stars layout

    RMGx01-AllStars-RemoveDeflicker.gct
        identical to the above but also disables the deflicker filter which
        blurs the image slightly

    RMGx01-Nvidia.gct
        a GCT which can be applied to your game's main.dol to give you the
        Nvidia layout

    RMGx01-Nvidia-RemoveDeflicker.gct
        identical to the above but also disables the deflicker filter which
        blurs the image slightly

--------
 Method
--------

0.  Consider running the wit and szs installers, it really makes both apps much
    easier to use.
        You can also just type in all the paths manually if you don't have
        admin rights on your PC or just don't wish to install them.
        The rest of this guide will assume you have installed both apps.
        Adjust if necessary.

1.  Extract this archive into a directory with your Super Mario Galaxy disc
    image.
        For example, I used 'C:\Games\Wii\Hacking\SuperMarioGalaxy'.

2.  Open a terminal/command prompt window in that directory.
        On modern versions of Windows, you can do this by opening a folder,
        clicking the address bar, where it says
            'This PC > Local Disk (C) > Games', etc.
        then typing 'cmd' (without quotes) and pressing Enter.

3.  Unpack your Super Mario Galaxy disc image.
        For example:
            wit extract --psel=data "RMGE01.wbfs" Galaxy1GamePad
        If your disc image is named something else, replace 'RMGE01.wbfs' with
        that file name.

4.  Apply your chosen GCT file to your extracted 'main.dol' file.
        For example:
            wstrt patch Galaxy1GamePad\sys\main.dol --add-section RMGE01-AllStars-RemoveDeflicker.gct
        Remember to replace the GCT filename with your region and variant.

5.  Repackage your extracted Super Mario Galaxy into a disc image.
        For example:
            wit copy Galaxy1GamePad Galaxy1GamePad.wbfs

6.  Using your newly patched Super Mario Galaxy disc image, create a Wii VC
    injection with Classic Controller emulation enabled.
        At this point, the process is the same as injecting any other game with
        Classic Controller support. You do not need the 'Force Classic
        Controller Connected' option, Classic Controller emulation is fine.

-----------
 Changelog
-----------

1.2
    Added Japan and Korea versions

1.1
    Added Europe version

1.0
    Initial release