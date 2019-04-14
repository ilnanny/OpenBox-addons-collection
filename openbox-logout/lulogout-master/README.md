# lulogout
Gtk3 Lua logout box, inspired by oblogout and made for my awesomewm config but without being dependent on the wm framework.

## Config

`config.lua` must be in the same folder as `lulogout`
```
style = {
    -- Controls opacity of window
    opacity = 0.5;
    -- Controls background color of screen
    bgcolor = "0,0,0";
    -- Icon theme
    theme = "simplistic";
    -- Each item is a button, "Label, Icon, Shortcut Key, Command"
    buttons = { 
        "Cancel,cancel,q,:cancel",
        "Lock,lock,l,i3lock",
        "Suspend,suspend,s,systemctl start suspend",
        "Hibernate,hibernate,h,systemctl start hibernate",
        "Restart,restart,r,systemctl start reboot",
        "Shutdown,shutdown,p,systemctl start poweroff"
     };
}
```

![lulogout](https://github.com/Jguer/jguer.github.io/blob/master/lulogout/lulogout.png?raw=true "Default settings")
